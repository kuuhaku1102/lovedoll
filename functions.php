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
