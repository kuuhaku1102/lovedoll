<?php
/**
 * Theme Setup Functions
 */

if ( ! function_exists( 'lovedoll_theme_setup' ) ) :
    function lovedoll_theme_setup() {
        // Add default posts and comments RSS feed links to head.
        add_theme_support( 'automatic-feed-links' );

        // Let WordPress manage the document title.
        add_theme_support( 'title-tag' );

        // Enable support for Post Thumbnails on posts and pages.
        add_theme_support( 'post-thumbnails' );

        // Register Navigation Menus
        register_nav_menus( array(
            'primary' => esc_html__( 'Primary Menu', 'lovedoll-premium' ),
            'footer'  => esc_html__( 'Footer Menu', 'lovedoll-premium' ),
        ) );

        // Add support for core custom logo.
        add_theme_support( 'custom-logo', array(
            'height'      => 250,
            'width'       => 250,
            'flex-width'  => true,
            'flex-height' => true,
        ) );
    }
endif;
add_action( 'after_setup_theme', 'lovedoll_theme_setup' );

/**
 * Enqueue scripts and styles.
 */
/**
 * Enqueue scripts and styles.
 */
function lovedoll_scripts() {
    wp_enqueue_style( 'lovedoll-style', get_stylesheet_uri() );
    
    // Google Fonts
    wp_enqueue_style( 'google-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Playfair+Display:wght@400;700&display=swap', array(), null );

    // Navigation JS
    wp_enqueue_script( 'lovedoll-navigation', get_template_directory_uri() . '/js/navigation.js', array(), '1.0.0', true );
}
add_action( 'wp_enqueue_scripts', 'lovedoll_scripts' );

/**
 * Register Custom Post Types
 */
function lovedoll_register_cpt() {
    $labels = array(
        'name'                  => _x( 'Dolls', 'Post Type General Name', 'lovedoll-premium' ),
        'singular_name'         => _x( 'Doll', 'Post Type Singular Name', 'lovedoll-premium' ),
        'menu_name'             => __( 'Dolls', 'lovedoll-premium' ),
        'all_items'             => __( 'All Dolls', 'lovedoll-premium' ),
        'add_new_item'          => __( 'Add New Doll', 'lovedoll-premium' ),
        'new_item'              => __( 'New Doll', 'lovedoll-premium' ),
    );
    $args = array(
        'label'                 => __( 'Doll', 'lovedoll-premium' ),
        'labels'                => $labels,
        'supports'              => array( 'title', 'editor', 'thumbnail', 'custom-fields', 'excerpt' ),
        'taxonomies'            => array( 'category', 'post_tag' ),
        'hierarchical'          => false,
        'public'                => true,
        'show_ui'               => true,
        'show_in_menu'          => true,
        'menu_position'         => 5,
        'menu_icon'             => 'dashicons-heart',
        'show_in_admin_bar'     => true,
        'show_in_nav_menus'     => true,
        'can_export'            => true,
        'has_archive'           => true,
        'exclude_from_search'   => false,
        'publicly_queryable'    => true,
        'capability_type'       => 'post',
    );
    register_post_type( 'dolls', $args );
}
add_action( 'init', 'lovedoll_register_cpt', 0 );

/**
 * Register Ranking Custom Post Type
 */
function lovedoll_register_ranking_cpt() {
    $labels = array(
        'name'                  => _x( 'Website Rankings', 'Post Type General Name', 'lovedoll-premium' ),
        'singular_name'         => _x( 'Website Ranking', 'Post Type Singular Name', 'lovedoll-premium' ),
        'menu_name'             => __( 'Website Rankings', 'lovedoll-premium' ),
        'all_items'             => __( 'All Rankings', 'lovedoll-premium' ),
        'add_new_item'          => __( 'Add New Ranking', 'lovedoll-premium' ),
        'new_item'              => __( 'New Ranking', 'lovedoll-premium' ),
        'edit_item'             => __( 'Edit Ranking', 'lovedoll-premium' ),
        'view_item'             => __( 'View Ranking', 'lovedoll-premium' ),
    );
    $args = array(
        'label'                 => __( 'Website Ranking', 'lovedoll-premium' ),
        'labels'                => $labels,
        'supports'              => array( 'title', 'thumbnail' ),
        'hierarchical'          => false,
        'public'                => true,
        'show_ui'               => true,
        'show_in_menu'          => true,
        'menu_position'         => 6,
        'menu_icon'             => 'dashicons-star-filled',
        'show_in_admin_bar'     => true,
        'show_in_nav_menus'     => false,
        'can_export'            => true,
        'has_archive'           => false,
        'exclude_from_search'   => true,
        'publicly_queryable'    => false,
        'capability_type'       => 'post',
    );
    register_post_type( 'website_ranking', $args );
}
add_action( 'init', 'lovedoll_register_ranking_cpt', 0 );

/**
 * Add Meta Boxes for Website Ranking
 */
function lovedoll_ranking_meta_boxes() {
    add_meta_box(
        'ranking_details',
        __( 'Ranking Details', 'lovedoll-premium' ),
        'lovedoll_ranking_meta_box_callback',
        'website_ranking',
        'normal',
        'high'
    );
}
add_action( 'add_meta_boxes', 'lovedoll_ranking_meta_boxes' );

/**
 * Meta Box Callback Function
 */
function lovedoll_ranking_meta_box_callback( $post ) {
    wp_nonce_field( 'lovedoll_ranking_meta_box', 'lovedoll_ranking_meta_box_nonce' );
    
    $rating = get_post_meta( $post->ID, '_ranking_rating', true );
    $affiliate_link = get_post_meta( $post->ID, '_ranking_affiliate_link', true );
    $rank_order = get_post_meta( $post->ID, '_ranking_order', true );
    ?>
    <table class="form-table">
        <tr>
            <th><label for="ranking_order"><?php _e( 'Rank Order', 'lovedoll-premium' ); ?></label></th>
            <td>
                <input type="number" id="ranking_order" name="ranking_order" value="<?php echo esc_attr( $rank_order ); ?>" min="1" max="10" class="regular-text" />
                <p class="description"><?php _e( 'Enter the ranking position (1-10)', 'lovedoll-premium' ); ?></p>
            </td>
        </tr>
        <tr>
            <th><label for="ranking_rating"><?php _e( 'Star Rating', 'lovedoll-premium' ); ?></label></th>
            <td>
                <select id="ranking_rating" name="ranking_rating">
                    <option value=""><?php _e( 'Select Rating', 'lovedoll-premium' ); ?></option>
                    <?php for ( $i = 1; $i <= 5; $i++ ) : ?>
                        <option value="<?php echo $i; ?>" <?php selected( $rating, $i ); ?>>
                            <?php echo str_repeat( '★', $i ) . str_repeat( '☆', 5 - $i ); ?>
                        </option>
                    <?php endfor; ?>
                </select>
                <p class="description"><?php _e( 'Select star rating (1-5 stars)', 'lovedoll-premium' ); ?></p>
            </td>
        </tr>
        <tr>
            <th><label for="ranking_affiliate_link"><?php _e( 'Affiliate Link', 'lovedoll-premium' ); ?></label></th>
            <td>
                <input type="url" id="ranking_affiliate_link" name="ranking_affiliate_link" value="<?php echo esc_url( $affiliate_link ); ?>" class="large-text" placeholder="https://example.com" />
                <p class="description"><?php _e( 'Enter the affiliate link URL', 'lovedoll-premium' ); ?></p>
            </td>
        </tr>
    </table>
    <?php
}

/**
 * Save Meta Box Data
 */
function lovedoll_save_ranking_meta_box( $post_id ) {
    if ( ! isset( $_POST['lovedoll_ranking_meta_box_nonce'] ) ) {
        return;
    }
    if ( ! wp_verify_nonce( $_POST['lovedoll_ranking_meta_box_nonce'], 'lovedoll_ranking_meta_box' ) ) {
        return;
    }
    if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
        return;
    }
    if ( ! current_user_can( 'edit_post', $post_id ) ) {
        return;
    }
    
    if ( isset( $_POST['ranking_rating'] ) ) {
        update_post_meta( $post_id, '_ranking_rating', sanitize_text_field( $_POST['ranking_rating'] ) );
    }
    
    if ( isset( $_POST['ranking_affiliate_link'] ) ) {
        update_post_meta( $post_id, '_ranking_affiliate_link', esc_url_raw( $_POST['ranking_affiliate_link'] ) );
    }
    
    if ( isset( $_POST['ranking_order'] ) ) {
        update_post_meta( $post_id, '_ranking_order', intval( $_POST['ranking_order'] ) );
    }
}
add_action( 'save_post', 'lovedoll_save_ranking_meta_box' );

/**
 * Website Ranking Shortcode
 */
function lovedoll_website_ranking_shortcode( $atts ) {
    $atts = shortcode_atts( array(
        'limit' => 5,
    ), $atts );
    
    $args = array(
        'post_type'      => 'website_ranking',
        'posts_per_page' => intval( $atts['limit'] ),
        'meta_key'       => '_ranking_order',
        'orderby'        => 'meta_value_num',
        'order'          => 'ASC',
        'post_status'    => 'publish',
    );
    
    $query = new WP_Query( $args );
    
    if ( ! $query->have_posts() ) {
        return '<p>' . __( 'No rankings found.', 'lovedoll-premium' ) . '</p>';
    }
    
    ob_start();
    ?>
    <div class="website-ranking-container">
        <?php while ( $query->have_posts() ) : $query->the_post(); 
            $rating = get_post_meta( get_the_ID(), '_ranking_rating', true );
            $affiliate_link = get_post_meta( get_the_ID(), '_ranking_affiliate_link', true );
            $rank_order = get_post_meta( get_the_ID(), '_ranking_order', true );
        ?>
        <div class="ranking-card">
            <div class="ranking-card-inner">
                <div class="ranking-badge">
                    <span class="rank-number"><?php echo esc_html( $rank_order ? $rank_order : '?' ); ?></span>
                    <span class="rank-label">位</span>
                </div>
                <div class="ranking-image">
                    <?php if ( has_post_thumbnail() ) : ?>
                        <?php the_post_thumbnail( 'medium', array( 'class' => 'ranking-thumbnail' ) ); ?>
                    <?php else : ?>
                        <div class="ranking-no-image">
                            <span>📷</span>
                        </div>
                    <?php endif; ?>
                </div>
                <div class="ranking-content">
                    <h3 class="ranking-title"><?php the_title(); ?></h3>
                    <?php if ( $rating ) : ?>
                        <div class="ranking-rating">
                            <?php 
                            for ( $i = 1; $i <= 5; $i++ ) {
                                echo $i <= $rating ? '★' : '☆';
                            }
                            ?>
                            <span class="rating-text">(<?php echo esc_html( $rating ); ?>/5)</span>
                        </div>
                    <?php endif; ?>
                    <?php if ( $affiliate_link ) : ?>
                        <div class="ranking-action">
                            <a href="<?php echo esc_url( $affiliate_link ); ?>" class="btn-ranking" target="_blank" rel="nofollow noopener">
                                公式サイトへ →
                            </a>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>
        <?php endwhile; ?>
    </div>
    <?php
    wp_reset_postdata();
    
    return ob_get_clean();
}
add_shortcode( 'website_ranking', 'lovedoll_website_ranking_shortcode' );
