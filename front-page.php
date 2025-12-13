<?php
/**
 * The template for displaying the front page
 */

get_header();
?>

<main id="primary" class="site-main">

    <!-- Hero Section -->
    <section class="hero-section text-center cute-hero" style="background-image: url('<?php echo get_template_directory_uri(); ?>/images/hero-bg.png'); background-size: cover; background-position: center;">
        <div class="container hero-overlay" style="background: rgba(255,255,255,0.85); padding: 3rem; border-radius: 20px;">
            <h1 class="hero-title"><?php esc_html_e('Find Your Internal Partner', 'lovedoll-premium'); ?></h1>
            <p class="hero-lead">
                国内正規品のラブドールを最安値で比較｜匿名配送で安心購入
            </p>
            <div class="hero-description slide-up">
                <p>初めてのラブドール選びでも失敗しないよう、<br>人気ランキング・価格比較・ショップの安全性を徹底調査しました。</p>
                <p>価格だけでなく、<br>品質・保証・アフターサポート・匿名配送の可否までしっかり比較し、<br><strong>あなたにとって最適な一体が必ず見つかります。</strong></p>
            </div>
            <div class="hero-buttons mt-4">
                <a href="#ranking" class="btn btn-primary btn-lg rounded-pill">🔥 人気ランキングを見る</a>
                <a href="#guide" class="btn btn-secondary btn-lg rounded-pill">🔰 失敗しない選び方を見る</a>
            </div>
        </div>
    </section>

    <!-- Recommended Items Shortcode -->
    <section id="recommended" class="section-padding container">
        <div class="section-header text-center mb-5">
            <span class="badge-cute">Recommended</span>
            <h2 class="section-title">💖 おすすめ商品一覧</h2>
            <p>厳選された最新のラブドールをご紹介</p>
        </div>
    <?php echo do_shortcode('[lovedoll_items]'); ?>
    </section>

    <!-- Website Ranking Section -->
    <section id="website-ranking" class="section-padding container">
        <div class="section-header text-center mb-5">
            <span class="badge-cute">Top Websites</span>
            <h2 class="section-title">🌐 おすすめウェブサイトランキング</h2>
            <p>信頼できる優良サイトを厳選してご紹介</p>
        </div>
        <?php echo do_shortcode('[website_ranking limit="5"]'); ?>
    </section>

    <!-- Popular Ranking -->
    <section id="ranking" class="section-padding container">
  <!-- 見出しだけ -->
    <div class="section-header text-center mb-5">
        <span class="badge-cute">Best Choice</span>
        <h2 class="section-title">🔥 今売れているラブドール TOP10</h2>
        <p>迷ったら、まずはここから。<br>
           口コミ評価・購入レビュー・満足度を総合してランキング形式で紹介。</p>
    </div>

    <!-- SweetDoll -->
    <h3 class="text-center mb-4">SweetDoll</h3>
    <?php echo do_shortcode('[lovedoll_items domain="sweet-doll.com"]'); ?>

    <!-- HappinessDoll -->
    <h3 class="text-center mt-5 mb-4">HappinessDoll</h3>
    <?php echo do_shortcode('[lovedoll_items domain="happiness-doll.com"]'); ?>

    <!-- YourDoll -->
    <h3 class="text-center mt-5 mb-4">YourDoll</h3>
    <?php echo do_shortcode('[lovedoll_items domain="yourdoll.jp"]'); ?>

        <div class="ranking-list">
            <?php
            // Mock Ranking Query (Replace with real logic Later)
            $args = array('post_type' => 'dolls', 'posts_per_page' => 3);
            $query = new WP_Query($args);
            $rank = 1;
            if ($query->have_posts()) :
                while ($query->have_posts()) : $query->the_post();
            ?>
            <div class="card ranking-card-horizontal mb-4">
                <div class="rank-badge rank-<?php echo $rank; ?>"><?php echo $rank; ?>位</div>
                <div class="row align-items-center">
                    <div class="col-img">
                        <?php if(has_post_thumbnail()) {
                            the_post_thumbnail('medium', ['class' => 'rounded']); 
                        } else {
                            // Use placeholder image
                            echo '<img src="' . get_template_directory_uri() . '/images/ranking-icon.png" class="rounded placeholder-img" alt="Rank ' . $rank . '">';
                        } ?>
                    </div>
                    <div class="col-content">
                        <h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
                        <p class="catchphrase text-pink">👑 <?php echo $rank === 1 ? '高評価・初心者にも人気' : ($rank === 2 ? '軽量で扱いやすい' : 'コスパ最強モデル'); ?></p>
                        <div class="excerpt"><?php the_excerpt(); ?></div>
                        <a href="<?php the_permalink(); ?>" class="btn btn-primary btn-block mt-2">詳細を見る</a>
                    </div>
                </div>
            </div>
            <?php 
                $rank++;
                endwhile;
                wp_reset_postdata();
            endif;
            ?>
        </div>
    </section>

    <!-- How to Choose -->
    <section id="guide" class="section-padding bg-cute-pattern">
        <div class="container">
            <div class="section-header text-center mb-5">
                <img src="<?php echo get_template_directory_uri(); ?>/images/guide-icon.png" alt="Guide" style="width: 50px; margin-bottom: 1rem;">
                <h2 class="section-title">🔰 ラブドールの選び方ガイド</h2>
                <p>初めてでも後悔しない！loveドールの選び方5つのポイント</p>
            </div>
            
            <div class="grid-3 guide-grid">
                <div class="card guide-box box-1">
                    <h3>① 材質</h3>
                    <p><strong>TPE</strong>：柔らかくリアル、価格が手頃<br><strong>シリコン</strong>：耐久性・質感が高い、価格は高め</p>
                </div>
                <div class="card guide-box box-2">
                    <h3>② 身長・体重</h3>
                    <p>目的や保管場所によって大きく変わるポイント。<br>扱いやすさを重視するなら <strong>25kg以下がおすすめ。</strong></p>
                </div>
                <div class="card guide-box box-3">
                    <h3>③ 骨格・可動域</h3>
                    <p>可動範囲が広いほどポージングの幅が広がる。<br>上級者は「二重関節仕様」も人気。</p>
                </div>
                <div class="card guide-box box-4">
                    <h3>④ カスタム性</h3>
                    <p>近年はカスタム自由度が高く、<br>顔の変更・ウィッグ変更・ボディ選択など多様。</p>
                </div>
                <div class="card guide-box box-5">
                    <h3>⑤ ショップの信頼性</h3>
                    <p>国内正規品取り扱い店なら<br>保証・返品・配送の安全性が段違い。</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Beginner Recommendations -->
    <section class="section-padding container">
        <div class="section-header text-center mb-5">
            <h2 class="section-title">🌱 初心者向けおすすめラブドール3選</h2>
            <p>ラブドールを初めて購入する方でも扱いやすい、<br>価格・重さ・メンテ性のバランスが良いモデルを厳選。</p>
        </div>
        
        <div class="grid-3">
            <div class="card recommend-card">
                <div class="card-header-pink">モデルA</div>
                <div class="card-body">
                    <h4>軽量で扱いやすい入門機</h4>
                    <p>初めてでも安心の軽さと価格設定。</p>
                    <a href="#" class="btn btn-sm btn-pink-outline">詳しく見る</a>
                </div>
            </div>
            <div class="card recommend-card">
                <div class="card-header-pink">モデルB</div>
                <div class="card-body">
                    <h4>人気No.1の万能タイプ</h4>
                    <p>バランスの取れたスペックで失敗なし。</p>
                    <a href="#" class="btn btn-sm btn-pink-outline">詳しく見る</a>
                </div>
            </div>
            <div class="card recommend-card">
                <div class="card-header-pink">モデルC</div>
                <div class="card-body">
                    <h4>コスパ重視で満足度が高い</h4>
                    <p>価格以上のクオリティを実現。</p>
                    <a href="#" class="btn btn-sm btn-pink-outline">詳しく見る</a>
                </div>
            </div>
        </div>
    </section>

    <!-- Usage Based & Campaign (Combined/Condensed for Space) -->
    <section class="section-padding bg-pink-light">
        <div class="container">
            <div class="grid-2">
                <div class="column-usage">
                    <h3 class="mb-4">✨ 用途別おすすめ</h3>
                    <ul class="cute-list">
                        <li><strong>軽量モデル</strong>：女性の負担を軽減したい方・持ち運び重視</li>
                        <li><strong>リアル系ハイエンド</strong>：リアルさ・造形美を求める方</li>
                        <li><strong>小型モデル</strong>：収納・保管スペースが限られている方</li>
                        <li><strong>予算別</strong>：10万円以下 / 20万円以上など</li>
                    </ul>
                    <a href="#" class="text-link">→ ［すべての特集を見る］</a>
                </div>
                <div class="column-campaign">
                    <h3 class="mb-4">🎁 お得なキャンペーン情報</h3>
                    <div class="campaign-box">
                        <p class="campaign-item">📢 <strong>〇〇ストア</strong>：最大20%OFF</p>
                        <p class="campaign-item">📢 <strong>〇〇メーカー</strong>：カスタム無料</p>
                        <p class="campaign-item">🚚 期間限定：<strong>匿名配送無料</strong></p>
                    </div>
                    <a href="#" class="text-link">→ ［もっと見る］</a>
                </div>
            </div>
        </div>
    </section>

    <!-- Shop Comparison -->
    <section class="section-padding container">
        <div class="section-header text-center mb-5">
            <h2 class="section-title">🏪 ラブドール販売店の徹底比較</h2>
            <p>大切なのは「本物を安全に購入できるか」。<br>特に初心者は <strong>国内正規品＋保証付き</strong> を推奨します。</p>
        </div>
        <div class="table-responsive">
            <table class="table table-cute w-100">
                <thead>
                    <tr>
                        <th>ショップ名</th>
                        <th>匿名配送</th>
                        <th>返品</th>
                        <th>価格</th>
                        <th>保証</th>
                        <th>特徴</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="fw-bold">Aストア</td>
                        <td class="text-success">○</td>
                        <td class="text-success">○</td>
                        <td>最安級</td>
                        <td>1年保証</td>
                        <td>国内正規・レビュー多数</td>
                    </tr>
                    <tr>
                        <td class="fw-bold">Bストア</td>
                        <td class="text-success">○</td>
                        <td class="text-warning">△</td>
                        <td>中程度</td>
                        <td>6ヶ月</td>
                        <td>カスタムが豊富</td>
                    </tr>
                    <tr>
                        <td class="text-muted">Cストア</td>
                        <td class="text-success">○</td>
                        <td class="text-danger">×</td>
                        <td>安い</td>
                        <td>なし</td>
                        <td>海外直送のため注意</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>

    <!-- Blog Articles Section -->
    <section id="blog" class="section-padding container">
        <div class="section-header text-center mb-5">
            <span class="badge-cute">Column</span>
            <h2 class="section-title">📝 コラム記事</h2>
            <p>ラブドールに関する役立つ情報をお届けします</p>
        </div>
        
        <div class="blog-grid">
            <?php
            $blog_args = array(
                'post_type' => 'post',
                'posts_per_page' => 6,
                'orderby' => 'date',
                'order' => 'DESC'
            );
            $blog_query = new WP_Query($blog_args);
            
            if ($blog_query->have_posts()) :
                while ($blog_query->have_posts()) : $blog_query->the_post();
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
                wp_reset_postdata();
            else :
                ?>
                <p class="text-center">まだ記事がありません。</p>
                <?php
            endif;
            ?>
        </div>
        
        <div class="text-center mt-5">
            <a href="<?php echo esc_url(home_url('/blog/')); ?>" class="btn btn-outline-pink btn-lg">すべての記事を見る →</a>
        </div>
    </section>

    <!-- Why Choose Us -->
    <section class="section-padding container">
        <div class="section-header text-center mb-5">
            <span class="badge-cute">Why Choose Us</span>
            <h2 class="section-title">💎 当サイトが選ばれる理由</h2>
            <p>安心・安全なラブドール選びをサポートします</p>
        </div>
        
        <div class="grid-3">
            <div class="feature-card">
                <div class="feature-icon">🔍</div>
                <h3 class="feature-title">徹底した比較調査</h3>
                <p class="feature-description">価格だけでなく、品質・保証・アフターサポートまで徹底的に比較。信頼できる情報のみを掲載しています。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">✅</div>
                <h3 class="feature-title">国内正規品のみ</h3>
                <p class="feature-description">国内正規代理店の商品のみを紹介。保証・返品対応がしっかりしているショップだけを厳選しています。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🚚</div>
                <h3 class="feature-title">匿名配送対応</h3>
                <p class="feature-description">プライバシーを重視し、匿名配送・無地梱包に対応したショップのみをご紹介。安心してご購入いただけます。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💰</div>
                <h3 class="feature-title">最安値保証</h3>
                <p class="feature-description">複数のショップを常時監視し、最安値情報を更新。お得なキャンペーン情報もいち早くお届けします。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3 class="feature-title">リアルな口コミ</h3>
                <p class="feature-description">実際の購入者のレビューや評価を集計。リアルな使用感や満足度を知ることができます。</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎓</div>
                <h3 class="feature-title">初心者サポート</h3>
                <p class="feature-description">初めての方でも安心して選べるよう、選び方ガイドやメンテナンス方法まで丁寧に解説しています。</p>
            </div>
        </div>
    </section>

    <!-- Customer Reviews -->
    <section class="section-padding bg-cute-pattern">
        <div class="container">
            <div class="section-header text-center mb-5">
                <span class="badge-cute">Reviews</span>
                <h2 class="section-title">💬 お客様の声</h2>
                <p>実際にご利用いただいた方々からの声をご紹介</p>
            </div>
            
            <div class="grid-3">
                <div class="review-card">
                    <div class="review-rating">★★★★★</div>
                    <p class="review-text">「初めてのラブドール購入でしたが、このサイトのランキングを参考にして大正解でした。匿名配送で安心して受け取れました。」</p>
                    <div class="review-author">
                        <span class="review-name">T.K様</span>
                        <span class="review-age">30代男性</span>
                    </div>
                </div>
                <div class="review-card">
                    <div class="review-rating">★★★★★</div>
                    <p class="review-text">「価格比較が分かりやすく、最安値で購入できました。選び方ガイドも参考になり、自分に合ったモデルを見つけられました。」</p>
                    <div class="review-author">
                        <span class="review-name">M.S様</span>
                        <span class="review-age">40代男性</span>
                    </div>
                </div>
                <div class="review-card">
                    <div class="review-rating">★★★★☆</div>
                    <p class="review-text">「国内正規品のみを扱っているので安心感があります。保証もしっかりしていて、アフターサポートも充実していました。」</p>
                    <div class="review-author">
                        <span class="review-name">H.Y様</span>
                        <span class="review-age">20代男性</span>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- FAQ -->
    <section class="section-padding container">
        <div class="section-header text-center mb-5">
            <span class="badge-cute">FAQ</span>
            <h2 class="section-title">❓ よくある質問</h2>
            <p>ラブドール購入に関する疑問にお答えします</p>
        </div>
        
        <div class="faq-container">
            <div class="faq-item">
                <div class="faq-question">
                    <span class="faq-icon">Q</span>
                    <h3>匿名配送で家族にバレませんか？</h3>
                </div>
                <div class="faq-answer">
                    <span class="faq-icon">A</span>
                    <p>大手販売店はすべて<strong>無地ダンボール</strong>で配送されます。商品名も「雑貨」「インテリア」などと記載され、中身が分からないよう配慮されています。また、営業所留めや時間指定も可能なショップが多いため、プライバシーは十分に守られます。</p>
                </div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">
                    <span class="faq-icon">Q</span>
                    <h3>重さはどれくらいですか？持ち運びは大変？</h3>
                </div>
                <div class="faq-answer">
                    <span class="faq-icon">A</span>
                    <p>モデルによって8kg〜40kgまで幅があります。初心者の方には<strong>25kg以下</strong>のモデルがおすすめです。軽量モデルは扱いやすく、メンテナンスや保管も楽になります。最近では15kg前後の高品質モデルも増えています。</p>
                </div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">
                    <span class="faq-icon">Q</span>
                    <h3>海外通販と国内通販、どっちが安全？</h3>
                </div>
                <div class="faq-answer">
                    <span class="faq-icon">A</span>
                    <p>国内通販のほうが、<strong>不良品対応・保証・配送リスクの低さ</strong>の面で圧倒的に安全です。海外通販は価格が安い場合もありますが、返品や修理が困難で、税関トラブルのリスクもあります。当サイトでは国内正規代理店のみをご紹介しています。</p>
                </div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">
                    <span class="faq-icon">Q</span>
                    <h3>メンテナンスは難しいですか？</h3>
                </div>
                <div class="faq-answer">
                    <span class="faq-icon">A</span>
                    <p>基本的なメンテナンスは<strong>使用後の洗浄とパウダーの塗布</strong>だけです。TPE素材は特に簡単で、シリコン素材も専用のクリーナーを使えば問題ありません。各ショップでメンテナンスキットも販売されており、初心者でも安心して管理できます。</p>
                </div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">
                    <span class="faq-icon">Q</span>
                    <h3>保証期間はどれくらいですか？</h3>
                </div>
                <div class="faq-answer">
                    <span class="faq-icon">A</span>
                    <p>国内正規店では<strong>6ヶ月〜1年の保証</strong>が一般的です。初期不良や製造上の欠陥については無償で修理・交換対応してもらえます。保証内容はショップによって異なるため、購入前に必ず確認しましょう。</p>
                </div>
            </div>
            
            <div class="faq-item">
                <div class="faq-question">
                    <span class="faq-icon">Q</span>
                    <h3>TPEとシリコン、どちらがおすすめ？</h3>
                </div>
                <div class="faq-answer">
                    <span class="faq-icon">A</span>
                    <p><strong>TPE</strong>は柔らかくリアルな触感で価格も手頃ですが、耐久性はやや劣ります。<strong>シリコン</strong>は耐久性・質感が高く、メンテナンスも楽ですが、価格は高めです。初心者にはコスパの良いTPEがおすすめですが、長期使用を考えるならシリコンも検討する価値があります。</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Purchase Flow -->
    <section class="section-padding bg-pink-light">
        <div class="container">
            <div class="section-header text-center mb-5">
                <span class="badge-cute">How to Buy</span>
                <h2 class="section-title">📦 購入までの流れ</h2>
                <p>初めての方でも安心してご購入いただけます</p>
            </div>
            
            <div class="purchase-flow">
                <div class="flow-step">
                    <div class="flow-number">1</div>
                    <h3 class="flow-title">ランキングから選ぶ</h3>
                    <p class="flow-description">人気ランキングや選び方ガイドを参考に、自分に合ったモデルを選びます。</p>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="flow-number">2</div>
                    <h3 class="flow-title">公式サイトで注文</h3>
                    <p class="flow-description">気に入ったモデルが見つかったら、公式サイトで注文。匿名配送を選択できます。</p>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="flow-number">3</div>
                    <h3 class="flow-title">安心の配送</h3>
                    <p class="flow-description">無地ダンボールで自宅に配送。営業所留めも可能です。</p>
                </div>
                <div class="flow-arrow">→</div>
                <div class="flow-step">
                    <div class="flow-number">4</div>
                    <h3 class="flow-title">開封・使用開始</h3>
                    <p class="flow-description">付属のマニュアルに従って開封。メンテナンスキットも同梱されています。</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Final CTA -->
    <section class="cta-section">
        <div class="container">
            <div class="cta-content">
                <h2 class="cta-title">迷ったら人気ランキングから選ぶのが最短ルートです</h2>
                <p class="cta-description">口コミ評価・満足度から「売れている＝失敗しにくい」モデルだけを厳選。<br>初心者の方でも安心して選べるよう、詳しい解説付きでご紹介しています。</p>
                <div class="cta-buttons">
                    <a href="#ranking" class="btn btn-primary btn-lg">🏆 人気ランキングを見る</a>
                    <a href="#guide" class="btn btn-secondary btn-lg">🔰 選び方ガイドを見る</a>
                </div>
            </div>
        </div>
    </section>

</main><!-- #main -->

<?php
get_footer();
