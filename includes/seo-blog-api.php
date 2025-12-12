<?php
/**
 * SEO Blog API Endpoints
 * 
 * Custom REST API endpoints for AI-generated blog posts
 */

/**
 * Register custom REST API routes
 */
function lovedoll_register_seo_blog_routes() {
    register_rest_route( 'lovedoll/v1', '/create-blog-post', array(
        'methods'             => 'POST',
        'callback'            => 'lovedoll_create_blog_post',
        'permission_callback' => '__return_true', // Change this in production
    ) );
    
    register_rest_route( 'lovedoll/v1', '/blog-posts', array(
        'methods'             => 'GET',
        'callback'            => 'lovedoll_get_blog_posts',
        'permission_callback' => '__return_true',
    ) );
}
add_action( 'rest_api_init', 'lovedoll_register_seo_blog_routes' );

/**
 * Create a new blog post
 * 
 * @param WP_REST_Request $request
 * @return WP_REST_Response
 */
function lovedoll_create_blog_post( $request ) {
    $params = $request->get_json_params();
    
    // Validate required fields
    if ( empty( $params['title'] ) || empty( $params['content'] ) ) {
        return new WP_REST_Response(
            array( 'error' => 'Title and content are required' ),
            400
        );
    }
    
    // Prepare post data
    $post_data = array(
        'post_title'   => sanitize_text_field( $params['title'] ),
        'post_content' => wp_kses_post( $params['content'] ),
        'post_status'  => isset( $params['status'] ) ? sanitize_text_field( $params['status'] ) : 'draft',
        'post_type'    => 'post',
        'post_excerpt' => isset( $params['excerpt'] ) ? sanitize_text_field( $params['excerpt'] ) : '',
    );
    
    // Insert the post
    $post_id = wp_insert_post( $post_data );
    
    if ( is_wp_error( $post_id ) ) {
        return new WP_REST_Response(
            array( 'error' => $post_id->get_error_message() ),
            500
        );
    }
    
    // Add meta description if provided
    if ( ! empty( $params['meta_description'] ) ) {
        update_post_meta( $post_id, '_yoast_wpseo_metadesc', sanitize_text_field( $params['meta_description'] ) );
    }
    
    // Add tags if provided
    if ( ! empty( $params['tags'] ) && is_array( $params['tags'] ) ) {
        wp_set_post_tags( $post_id, $params['tags'], false );
    }
    
    // Add categories if provided
    if ( ! empty( $params['categories'] ) && is_array( $params['categories'] ) ) {
        wp_set_post_categories( $post_id, $params['categories'], false );
    }
    
    // Add custom meta for AI-generated flag
    update_post_meta( $post_id, '_ai_generated', true );
    update_post_meta( $post_id, '_ai_generated_date', current_time( 'mysql' ) );
    
    if ( ! empty( $params['keyword'] ) ) {
        update_post_meta( $post_id, '_target_keyword', sanitize_text_field( $params['keyword'] ) );
    }
    
    // Get the post permalink
    $permalink = get_permalink( $post_id );
    
    return new WP_REST_Response(
        array(
            'success'   => true,
            'post_id'   => $post_id,
            'permalink' => $permalink,
            'title'     => $params['title'],
            'status'    => $post_data['post_status'],
        ),
        201
    );
}

/**
 * Get AI-generated blog posts
 * 
 * @param WP_REST_Request $request
 * @return WP_REST_Response
 */
function lovedoll_get_blog_posts( $request ) {
    $params = $request->get_params();
    
    $args = array(
        'post_type'      => 'post',
        'posts_per_page' => isset( $params['per_page'] ) ? intval( $params['per_page'] ) : 10,
        'paged'          => isset( $params['page'] ) ? intval( $params['page'] ) : 1,
        'meta_query'     => array(
            array(
                'key'     => '_ai_generated',
                'value'   => true,
                'compare' => '=',
            ),
        ),
    );
    
    $query = new WP_Query( $args );
    
    $posts = array();
    
    if ( $query->have_posts() ) {
        while ( $query->have_posts() ) {
            $query->the_post();
            
            $post_id = get_the_ID();
            
            $posts[] = array(
                'id'              => $post_id,
                'title'           => get_the_title(),
                'excerpt'         => get_the_excerpt(),
                'permalink'       => get_permalink(),
                'date'            => get_the_date( 'c' ),
                'status'          => get_post_status(),
                'target_keyword'  => get_post_meta( $post_id, '_target_keyword', true ),
                'ai_generated_date' => get_post_meta( $post_id, '_ai_generated_date', true ),
            );
        }
        wp_reset_postdata();
    }
    
    return new WP_REST_Response(
        array(
            'posts'       => $posts,
            'total'       => $query->found_posts,
            'total_pages' => $query->max_num_pages,
        ),
        200
    );
}

/**
 * Add AI-generated column to posts list
 */
function lovedoll_add_ai_generated_column( $columns ) {
    $columns['ai_generated'] = __( 'AI Generated', 'lovedoll-premium' );
    return $columns;
}
add_filter( 'manage_posts_columns', 'lovedoll_add_ai_generated_column' );

/**
 * Display AI-generated column content
 */
function lovedoll_display_ai_generated_column( $column, $post_id ) {
    if ( $column === 'ai_generated' ) {
        $is_ai = get_post_meta( $post_id, '_ai_generated', true );
        if ( $is_ai ) {
            $keyword = get_post_meta( $post_id, '_target_keyword', true );
            echo '✓ AI';
            if ( $keyword ) {
                echo '<br><small>' . esc_html( $keyword ) . '</small>';
            }
        } else {
            echo '—';
        }
    }
}
add_action( 'manage_posts_custom_column', 'lovedoll_display_ai_generated_column', 10, 2 );
