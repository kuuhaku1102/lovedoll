<?php
/**
 * REST API endpoints for ingesting external product data (kuma-doll.com, etc.).
 *
 * - Adds /wp-json/lovedoll/v1/add-item for creating posts.
 * - Adds /wp-json/lovedoll/v1/list for returning existing items (for duplicate checks).
 * - Handles kuma-doll.com hotlink protection by downloading and sideloading images on WP.
 */

if ( ! defined( 'ABSPATH' ) ) {
    exit;
}

/**
 * Download kuma-doll images server-side and register them as media.
 *
 * This follows the required flow for avoiding hotlink/placeholder images on kuma-doll.com:
 * 1. download_url()
 * 2. media_handle_sideload()
 * 3. return WordPress media URL
 *
 * @param string $url
 * @param string $title
 * @return string|false Attachment URL on success, false on failure.
 */
function lid_fetch_image_with_referer( $url, $title ) {
    require_once ABSPATH . 'wp-admin/includes/file.php';
    require_once ABSPATH . 'wp-admin/includes/media.php';
    require_once ABSPATH . 'wp-admin/includes/image.php';

    $tmp = download_url( $url );

    if ( is_wp_error( $tmp ) ) {
        return false;
    }

    $file = [
        'name'     => sanitize_file_name( $title ) . '.webp',
        'type'     => 'image/webp',
        'tmp_name' => $tmp,
        'error'    => 0,
        'size'     => filesize( $tmp ),
    ];

    $attachment_id = media_handle_sideload( $file, 0 );
    @unlink( $tmp );

    if ( is_wp_error( $attachment_id ) ) {
        return false;
    }

    return wp_get_attachment_url( $attachment_id );
}

/**
 * Normalize price to integer.
 *
 * @param mixed $value
 * @return int|null
 */
function lovedoll_normalize_price( $value ) {
    if ( is_numeric( $value ) ) {
        return (int) $value;
    }
    $digits = preg_replace( '/[^0-9]/', '', (string) $value );
    if ( '' === $digits ) {
        return null;
    }
    return (int) $digits;
}

/**
 * Build a REST-friendly response payload for a product post.
 */
function lovedoll_build_product_payload( $post_id ) {
    $product_url = get_post_meta( $post_id, '_product_url', true );
    $price       = (int) get_post_meta( $post_id, '_price', true );
    $image_url   = get_post_meta( $post_id, '_final_image_url', true );

    if ( ! $image_url ) {
        $thumb_id = get_post_thumbnail_id( $post_id );
        if ( $thumb_id ) {
            $image_url = wp_get_attachment_url( $thumb_id );
        }
    }

    return [
        'id'          => $post_id,
        'title'       => get_the_title( $post_id ),
        'product_url' => $product_url,
        'price'       => $price,
        'image_url'   => $image_url,
    ];
}

/**
 * REST callback: list products for duplicate checks.
 */
function lovedoll_list_items() {
    $query = new WP_Query(
        [
            'post_type'      => 'dolls',
            'post_status'    => 'publish',
            'posts_per_page' => 200,
            'fields'         => 'ids',
        ]
    );

    $items = [];
    foreach ( $query->posts as $post_id ) {
        $items[] = lovedoll_build_product_payload( $post_id );
    }

    return $items;
}

/**
 * REST callback: ingest a product item.
 */
function lovedoll_add_item( WP_REST_Request $request ) {
    $title         = sanitize_text_field( $request->get_param( 'title' ) );
    $raw_price     = $request->get_param( 'price' );
    $image_src     = esc_url_raw( $request->get_param( 'image_url' ) );
    $product_url   = esc_url_raw( $request->get_param( 'product_url' ) );
    $image_content = $request->get_param( 'image_content' );
    $image_name    = sanitize_file_name( $request->get_param( 'image_name' ) );

    $price = lovedoll_normalize_price( $raw_price );

    if ( ! $title || ! $price || ! $image_src || ! $product_url ) {
        return new WP_Error( 'invalid_params', 'title, price, image_url, and product_url are required', [ 'status' => 400 ] );
    }

    // Skip very high prices (>= 1,000,000) for consistency with scrapers.
    if ( $price >= 1000000 ) {
        return new WP_Error( 'price_too_high', 'Price is 1,000,000 or higher; skipped.', [ 'status' => 422 ] );
    }

    // Deduplicate by product_url.
    $existing = new WP_Query(
        [
            'post_type'  => 'dolls',
            'meta_query' => [
                [
                    'key'   => '_product_url',
                    'value' => $product_url,
                ],
            ],
            'fields'     => 'ids',
        ]
    );

    if ( $existing->have_posts() ) {
        $post_id = $existing->posts[0];
        return lovedoll_build_product_payload( $post_id );
    }

    // Create the post first.
    $post_id = wp_insert_post(
        [
            'post_title'   => $title,
            'post_status'  => 'publish',
            'post_type'    => 'dolls',
            'post_content' => '',
        ],
        true
    );

    if ( is_wp_error( $post_id ) ) {
        return $post_id;
    }

    update_post_meta( $post_id, '_product_url', $product_url );
    update_post_meta( $post_id, '_price', $price );
    update_post_meta( $post_id, '_source_image_url', $image_src );

    // Handle image sideloading with kuma-doll hotlink protection.
    require_once ABSPATH . 'wp-admin/includes/file.php';
    require_once ABSPATH . 'wp-admin/includes/media.php';
    require_once ABSPATH . 'wp-admin/includes/image.php';

    $final_image_url = $image_src;
    $thumbnail_id    = null;

    // Prefer direct binary provided by scraper (base64-encoded image_content).
    if ( $image_content ) {
        $decoded = base64_decode( $image_content );
        if ( false !== $decoded ) {
            $tmp = wp_tempnam( $image_name ? $image_name : 'kuma-image' );
            if ( $tmp && false !== file_put_contents( $tmp, $decoded ) ) {
                $filetype = wp_check_filetype( $image_name );
                $file     = [
                    'name'     => $image_name ? $image_name : 'kuma-image.webp',
                    'type'     => $filetype && $filetype['type'] ? $filetype['type'] : 'image/webp',
                    'tmp_name' => $tmp,
                    'error'    => 0,
                    'size'     => filesize( $tmp ),
                ];

                $attachment_id = media_handle_sideload( $file, $post_id, $title, 'id' );
                @unlink( $tmp );

                if ( ! is_wp_error( $attachment_id ) ) {
                    $thumbnail_id    = $attachment_id;
                    $final_image_url = wp_get_attachment_url( $attachment_id );
                }
            }
        }
    }

    // If binary was not supplied or failed, fall back to fetching by URL.
    if ( ! $thumbnail_id ) {
        if ( false !== strpos( $image_src, 'kuma-doll.com' ) ) {
            $saved = lid_fetch_image_with_referer( $image_src, $title );
            if ( $saved ) {
                $final_image_url = $saved;
                $thumbnail_id    = attachment_url_to_postid( $saved );
            }
        } else {
            $attachment_id = media_sideload_image( $image_src, $post_id, $title, 'id' );
            if ( ! is_wp_error( $attachment_id ) ) {
                $thumbnail_id    = $attachment_id;
                $final_image_url = wp_get_attachment_url( $attachment_id );
            }
        }
    }

    if ( $thumbnail_id && ! is_wp_error( $thumbnail_id ) ) {
        set_post_thumbnail( $post_id, $thumbnail_id );
    }

    update_post_meta( $post_id, '_final_image_url', $final_image_url );

    return lovedoll_build_product_payload( $post_id );
}

/**
 * Register REST routes.
 */
function lovedoll_register_product_routes() {
    register_rest_route(
        'lovedoll/v1',
        '/add-item',
        [
            'methods'             => WP_REST_Server::CREATABLE,
            'callback'            => 'lovedoll_add_item',
            'permission_callback' => '__return_true',
        ]
    );

    register_rest_route(
        'lovedoll/v1',
        '/list',
        [
            'methods'             => WP_REST_Server::READABLE,
            'callback'            => 'lovedoll_list_items',
            'permission_callback' => '__return_true',
        ]
    );
}
add_action( 'rest_api_init', 'lovedoll_register_product_routes' );
