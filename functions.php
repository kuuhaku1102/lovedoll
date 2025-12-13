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
    $description = get_post_meta( $post->ID, '_ranking_description', true );
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
                <input type="url" id="ranking_affiliate_link" name="ranking_affiliate_link" value="<?php echo esc_url( $affiliate_link ); ?>" class="regular-text" />
                <p class="description"><?php _e( 'Enter the affiliate link URL', 'lovedoll-premium' ); ?></p>
            </td>
        </tr>
        <tr>
            <th><label for="ranking_description"><?php _e( 'Description', 'lovedoll-premium' ); ?></label></th>
            <td>
                <textarea id="ranking_description" name="ranking_description" rows="5" class="large-text"><?php echo esc_textarea( $description ); ?></textarea>
                <p class="description"><?php _e( 'Enter a brief description or introduction for this ranking item', 'lovedoll-premium' ); ?></p>
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
    
    if ( isset( $_POST['ranking_description'] ) ) {
        update_post_meta( $post_id, '_ranking_description', wp_kses_post( $_POST['ranking_description'] ) );
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
            $description = get_post_meta( get_the_ID(), '_ranking_description', true );
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
                    <?php if ( $description ) : ?>
                        <div class="ranking-description">
                            <p><?php echo wp_kses_post( $description ); ?></p>
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

/**
 * Load SEO Blog API
 */
require_once get_template_directory() . '/includes/seo-blog-api.php';

/**
 * Add Column Menu Item to Primary Menu
 */
function lovedoll_add_column_menu_item($items, $args) {
    if ($args->theme_location == 'primary') {
        // Get blog page URL
        $blog_url = home_url('/blog/');
        
        // Add Column menu item
        $column_item = '<li class="menu-item menu-item-column"><a href="' . esc_url($blog_url) . '">📝 コラム</a></li>';
        $items .= $column_item;
    }
    return $items;
}
add_filter('wp_nav_menu_items', 'lovedoll_add_column_menu_item', 10, 2);

/**
 * Create Blog Archive Page on Theme Activation
 */
function lovedoll_create_blog_page() {
    // Check if blog page already exists
    $blog_page = get_page_by_path('blog');
    
    if (!$blog_page) {
        // Create blog page
        $blog_page_id = wp_insert_post(array(
            'post_title'    => 'コラム',
            'post_name'     => 'blog',
            'post_content'  => '',
            'post_status'   => 'publish',
            'post_type'     => 'page',
            'post_author'   => 1,
        ));
        
        // Set as posts page
        if ($blog_page_id && !is_wp_error($blog_page_id)) {
            update_option('page_for_posts', $blog_page_id);
        }
    }
}
add_action('after_switch_theme', 'lovedoll_create_blog_page');

/**
 * Flush Rewrite Rules on Theme Activation
 */
function lovedoll_flush_rewrite_rules() {
    flush_rewrite_rules();
}
add_action('after_switch_theme', 'lovedoll_flush_rewrite_rules');

/**
 * Ensure Post Permalinks Work Correctly
 */
function lovedoll_fix_post_permalinks() {
    // Check if we need to flush rewrite rules
    $flush_needed = get_option('lovedoll_flush_rewrite_rules');
    if ($flush_needed !== 'done') {
        flush_rewrite_rules(true);
        update_option('lovedoll_flush_rewrite_rules', 'done');
    }
}
add_action('init', 'lovedoll_fix_post_permalinks', 999);

/**
 * Disable Comments Completely
 */
// Disable support for comments and trackbacks in post types
function lovedoll_disable_comments_post_types_support() {
    $post_types = get_post_types();
    foreach ($post_types as $post_type) {
        if(post_type_supports($post_type, 'comments')) {
            remove_post_type_support($post_type, 'comments');
            remove_post_type_support($post_type, 'trackbacks');
        }
    }
}
add_action('admin_init', 'lovedoll_disable_comments_post_types_support');

// Close comments on the front-end
function lovedoll_disable_comments_status() {
    return false;
}
add_filter('comments_open', 'lovedoll_disable_comments_status', 20, 2);
add_filter('pings_open', 'lovedoll_disable_comments_status', 20, 2);

// Hide existing comments
function lovedoll_disable_comments_hide_existing_comments($comments) {
    $comments = array();
    return $comments;
}
add_filter('comments_array', 'lovedoll_disable_comments_hide_existing_comments', 10, 2);

// Remove comments page in menu
function lovedoll_disable_comments_admin_menu() {
    remove_menu_page('edit-comments.php');
}
add_action('admin_menu', 'lovedoll_disable_comments_admin_menu');

// Redirect any user trying to access comments page
function lovedoll_disable_comments_admin_menu_redirect() {
    global $pagenow;
    if ($pagenow === 'edit-comments.php') {
        wp_redirect(admin_url());
        exit;
    }
}
add_action('admin_init', 'lovedoll_disable_comments_admin_menu_redirect');

// Remove comments metabox from dashboard
function lovedoll_disable_comments_dashboard() {
    remove_meta_box('dashboard_recent_comments', 'dashboard', 'normal');
}
add_action('admin_init', 'lovedoll_disable_comments_dashboard');

// Remove comments links from admin bar
function lovedoll_disable_comments_admin_bar() {
    if (is_admin_bar_showing()) {
        remove_action('admin_bar_menu', 'wp_admin_bar_comments_menu', 60);
    }
}
add_action('init', 'lovedoll_disable_comments_admin_bar');

/**
 * Add Structured Data (Schema.org) for SEO
 */
function lovedoll_add_structured_data() {
    if (is_singular('post')) {
        global $post;
        
        $schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'Article',
            'headline' => get_the_title(),
            'description' => has_excerpt() ? get_the_excerpt() : wp_trim_words(get_the_content(), 30),
            'author' => array(
                '@type' => 'Organization',
                'name' => get_bloginfo('name')
            ),
            'publisher' => array(
                '@type' => 'Organization',
                'name' => get_bloginfo('name'),
                'logo' => array(
                    '@type' => 'ImageObject',
                    'url' => get_template_directory_uri() . '/images/logo.png'
                )
            ),
            'datePublished' => get_the_date('c'),
            'dateModified' => get_the_modified_date('c'),
            'mainEntityOfPage' => array(
                '@type' => 'WebPage',
                '@id' => get_permalink()
            )
        );
        
        if (has_post_thumbnail()) {
            $schema['image'] = get_the_post_thumbnail_url(get_the_ID(), 'full');
        }
        
        echo '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>' . "\n";
    }
    
    if (is_home() || is_front_page()) {
        $schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'WebSite',
            'name' => get_bloginfo('name'),
            'description' => get_bloginfo('description'),
            'url' => home_url('/'),
            'potentialAction' => array(
                '@type' => 'SearchAction',
                'target' => home_url('/?s={search_term_string}'),
                'query-input' => 'required name=search_term_string'
            )
        );
        
        echo '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>' . "\n";
    }
    
    // BreadcrumbList Schema
    if (!is_front_page()) {
        $breadcrumb_schema = array(
            '@context' => 'https://schema.org',
            '@type' => 'BreadcrumbList',
            'itemListElement' => array()
        );
        
        $position = 1;
        
        // Home
        $breadcrumb_schema['itemListElement'][] = array(
            '@type' => 'ListItem',
            'position' => $position++,
            'name' => 'ホーム',
            'item' => home_url('/')
        );
        
        if (is_singular()) {
            $categories = get_the_category();
            if ($categories) {
                $breadcrumb_schema['itemListElement'][] = array(
                    '@type' => 'ListItem',
                    'position' => $position++,
                    'name' => $categories[0]->name,
                    'item' => get_category_link($categories[0]->term_id)
                );
            }
            
            $breadcrumb_schema['itemListElement'][] = array(
                '@type' => 'ListItem',
                'position' => $position++,
                'name' => get_the_title(),
                'item' => get_permalink()
            );
        } elseif (is_category()) {
            $breadcrumb_schema['itemListElement'][] = array(
                '@type' => 'ListItem',
                'position' => $position++,
                'name' => single_cat_title('', false),
                'item' => get_category_link(get_queried_object_id())
            );
        }
        
        echo '<script type="application/ld+json">' . json_encode($breadcrumb_schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) . '</script>' . "\n";
    }
}
add_action('wp_head', 'lovedoll_add_structured_data');

/**
 * Add Breadcrumb Navigation
 */
function lovedoll_breadcrumb() {
    if (is_front_page()) {
        return;
    }
    
    echo '<nav class="breadcrumb-nav" aria-label="パンくずリスト">';
    echo '<ol class="breadcrumb">';
    echo '<li class="breadcrumb-item"><a href="' . home_url('/') . '">ホーム</a></li>';
    
    if (is_singular()) {
        $categories = get_the_category();
        if ($categories) {
            echo '<li class="breadcrumb-item"><a href="' . get_category_link($categories[0]->term_id) . '">' . $categories[0]->name . '</a></li>';
        }
        echo '<li class="breadcrumb-item active" aria-current="page">' . get_the_title() . '</li>';
    } elseif (is_category()) {
        echo '<li class="breadcrumb-item active" aria-current="page">' . single_cat_title('', false) . '</li>';
    } elseif (is_tag()) {
        echo '<li class="breadcrumb-item active" aria-current="page">' . single_tag_title('', false) . '</li>';
    } elseif (is_archive()) {
        echo '<li class="breadcrumb-item active" aria-current="page">' . post_type_archive_title('', false) . '</li>';
    } elseif (is_search()) {
        echo '<li class="breadcrumb-item active" aria-current="page">検索結果</li>';
    }
    
    echo '</ol>';
    echo '</nav>';
}

/**
 * ========================================
 * アフィリエイトリンク自動変換機能
 * ========================================
 */

// 管理画面を読み込み
require_once get_template_directory() . '/admin-affiliate-links.php';

/**
 * フロントエンドに JavaScript を読み込み
 */
function lovedoll_enqueue_affiliate_converter() {
    // 管理画面では読み込まない
    if (is_admin()) {
        return;
    }

    // JavaScript ファイルを読み込み
    wp_enqueue_script(
        'lovedoll-affiliate-converter',
        get_template_directory_uri() . '/js/affiliate-link-converter.js',
        array(),
        '1.0.0',
        true
    );

    // 設定を JavaScript に渡す
    $affiliate_links = get_option('lovedoll_affiliate_links', array());
    
    wp_localize_script(
        'lovedoll-affiliate-converter',
        'lovedollAffiliateSettings',
        array(
            'links' => $affiliate_links
        )
    );
}
add_action('wp_enqueue_scripts', 'lovedoll_enqueue_affiliate_converter');

/**
 * デバッグ用：設定を確認する関数
 */
function lovedoll_get_affiliate_settings() {
    return get_option('lovedoll_affiliate_links', array());
}
