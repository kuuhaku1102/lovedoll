<?php
/**
 * The template for displaying archive pages
 */

get_header();
?>

<main id="primary" class="site-main container section-padding">

    <header class="page-header mb-4">
        <?php
        the_archive_title( '<h1 class="page-title">', '</h1>' );
        the_archive_description( '<div class="archive-description">', '</div>' );
        ?>
    </header><!-- .page-header -->

    <?php if ( have_posts() ) : ?>
        <div class="blog-grid">
            <?php
            while ( have_posts() ) :
                the_post();
                ?>
                <article class="blog-card">
                    <?php if (has_post_thumbnail()) : ?>
                        <a href="<?php the_permalink(); ?>" class="blog-thumbnail">
                            <?php the_post_thumbnail('medium'); ?>
                        </a>
                    <?php endif; ?>
                    <div class="blog-content">
                        <div class="blog-meta">
                            <span class="blog-date"><?php echo get_the_date('Y.m.d'); ?></span>
                            <?php
                            $categories = get_the_category();
                            if (!empty($categories)) {
                                echo '<span class="blog-category">' . esc_html($categories[0]->name) . '</span>';
                            }
                            ?>
                        </div>
                        <h3 class="blog-title">
                            <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                        </h3>
                        <div class="blog-excerpt">
                            <?php echo wp_trim_words(get_the_excerpt(), 30, '...'); ?>
                        </div>
                        <a href="<?php the_permalink(); ?>" class="blog-read-more">続きを読む →</a>
                    </div>
                </article>
                <?php
            endwhile;
            ?>
        </div>
        
        <div class="pagination">
            <?php the_posts_pagination(); ?>
        </div>

    <?php else : ?>
        <p>No posts found.</p>
    <?php endif; ?>

</main><!-- #main -->

<?php
get_footer();
