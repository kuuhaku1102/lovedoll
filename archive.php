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
        <div class="ranking-grid">
            <?php
            while ( have_posts() ) :
                the_post();
                ?>
                <div class="card ranking-card">
                    <div class="ranking-image">
                        <?php if (has_post_thumbnail()) {
                            the_post_thumbnail('medium');
                        } else {
                            echo '<div class="placeholder-img">No Image</div>';
                        } ?>
                    </div>
                    <div class="ranking-details">
                        <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
                        <div class="excerpt"><?php the_excerpt(); ?></div>
                        <a href="<?php the_permalink(); ?>" class="btn btn-sm btn-outline">Read More</a>
                    </div>
                </div>
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
