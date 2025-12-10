<?php
/**
 * The template for displaying the blog index (posts page)
 */

get_header();
?>

<main id="primary" class="site-main container section-padding">

    <header class="page-header mb-5 text-center">
        <h1 class="page-title section-title">
            <span class="en">BLOG</span>
            <span class="ja">ブログ</span>
        </h1>
        <p class="section-desc">最新情報やコラムをお届けします</p>
    </header>

    <?php if ( have_posts() ) : ?>
        <div class="blog-grid">
            <?php
            while ( have_posts() ) :
                the_post();
                ?>
                <article id="post-<?php the_ID(); ?>" <?php post_class('blog-card'); ?>>
                    <a href="<?php the_permalink(); ?>" class="blog-card-link">
                        <div class="blog-card-image">
                            <?php 
                            if (has_post_thumbnail()) {
                                the_post_thumbnail('medium_large');
                            } else {
                                echo '<div class="placeholder-img"><span class="dashicons dashicons-format-image"></span></div>';
                            } 
                            ?>
                            <div class="blog-card-meta-overlay">
                                <span class="posted-on"><?php echo get_the_date('Y.m.d'); ?></span>
                            </div>
                        </div>
                        <div class="blog-card-content">
                            <div class="blog-card-categories">
                                <?php
                                $categories = get_the_category();
                                if ( ! empty( $categories ) ) {
                                    echo '<span class="cat-label">' . esc_html( $categories[0]->name ) . '</span>';
                                }
                                ?>
                            </div>
                            <h2 class="blog-card-title"><?php the_title(); ?></h2>
                            <div class="blog-card-excerpt">
                                <?php echo wp_trim_words( get_the_excerpt(), 40, '...' ); ?>
                            </div>
                        </div>
                    </a>
                </article>
                <?php
            endwhile;
            ?>
        </div>
        
        <div class="pagination">
            <?php 
            the_posts_pagination( array(
                'mid_size'  => 2,
                'prev_text' => '&laquo;',
                'next_text' => '&raquo;',
            ) ); 
            ?>
        </div>

    <?php else : ?>
        <div class="no-results text-center">
            <p>記事が見つかりませんでした。</p>
        </div>
    <?php endif; ?>

</main><!-- #main -->

<?php
get_footer();
