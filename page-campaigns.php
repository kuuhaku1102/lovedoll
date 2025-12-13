<?php
/**
 * Template Name: キャンペーン情報
 */

get_header();
?>

<main id="primary" class="site-main">

    <?php lovedoll_breadcrumb(); ?>

    <div class="container section-padding">
        
        <!-- Page Header -->
        <header class="page-header text-center mb-5">
            <span class="badge-cute">Campaigns</span>
            <h1 class="page-title section-title">🎁 お得なキャンペーン情報</h1>
            <p class="page-description">最新のキャンペーンやセール情報をチェックして、お得に購入しましょう</p>
            <p class="update-date"><small>最終更新日: <?php echo date('Y年m月d日'); ?></small></p>
        </header>

        <!-- 現在開催中のキャンペーン -->
        <section class="campaign-section mb-5">
            <div class="section-header text-center mb-4">
                <h2 class="section-title">🔥 現在開催中のキャンペーン</h2>
            </div>
            
            <div class="campaign-grid">
                <!-- キャンペーン1 -->
                <div class="campaign-card hot">
                    <div class="campaign-badge">期間限定</div>
                    <div class="campaign-shop">
                        <h3>YourDoll</h3>
                        <span class="shop-tag">国内最大手</span>
                    </div>
                    <div class="campaign-content">
                        <h4 class="campaign-title">🎉 新春セール 最大20%OFF</h4>
                        <p class="campaign-description">人気モデルが期間限定で最大20%OFF！TPE製標準サイズが特にお得です。</p>
                        <div class="campaign-details">
                            <div class="detail-item">
                                <span class="detail-label">割引率</span>
                                <span class="detail-value">最大20%OFF</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">対象商品</span>
                                <span class="detail-value">TPE製全モデル</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">期間</span>
                                <span class="detail-value">2025年1月1日〜1月31日</span>
                            </div>
                        </div>
                        <a href="#" class="btn btn-primary btn-block mt-3">詳細を見る</a>
                    </div>
                </div>

                <!-- キャンペーン2 -->
                <div class="campaign-card">
                    <div class="campaign-badge">送料無料</div>
                    <div class="campaign-shop">
                        <h3>DachiWife</h3>
                        <span class="shop-tag">安心の正規代理店</span>
                    </div>
                    <div class="campaign-content">
                        <h4 class="campaign-title">🚚 全商品送料無料キャンペーン</h4>
                        <p class="campaign-description">通常5,000円の送料が無料に！さらに匿名配送も無料で対応します。</p>
                        <div class="campaign-details">
                            <div class="detail-item">
                                <span class="detail-label">特典</span>
                                <span class="detail-value">送料無料 + 匿名配送無料</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">対象商品</span>
                                <span class="detail-value">全商品</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">期間</span>
                                <span class="detail-value">2025年1月15日〜2月15日</span>
                            </div>
                        </div>
                        <a href="#" class="btn btn-primary btn-block mt-3">詳細を見る</a>
                    </div>
                </div>

                <!-- キャンペーン3 -->
                <div class="campaign-card">
                    <div class="campaign-badge">カスタム無料</div>
                    <div class="campaign-shop">
                        <h3>TPDOLL</h3>
                        <span class="shop-tag">カスタマイズ豊富</span>
                    </div>
                    <div class="campaign-content">
                        <h4 class="campaign-title">🎨 カスタマイズオプション無料</h4>
                        <p class="campaign-description">通常有料のカスタマイズオプション（メイク、ウィッグ、目の色など）が無料に！</p>
                        <div class="campaign-details">
                            <div class="detail-item">
                                <span class="detail-label">特典</span>
                                <span class="detail-value">カスタムオプション3つまで無料</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">対象商品</span>
                                <span class="detail-value">シリコン製モデル</span>
                            </div>
                            <div class="detail-item">
                                <span class="detail-label">期間</span>
                                <span class="detail-value">2025年1月10日〜1月31日</span>
                            </div>
                        </div>
                        <a href="#" class="btn btn-primary btn-block mt-3">詳細を見る</a>
                    </div>
                </div>
            </div>
        </section>

        <!-- 定期開催のキャンペーン -->
        <section class="campaign-section mb-5">
            <div class="section-header text-center mb-4">
                <h2 class="section-title">📅 定期開催のキャンペーン</h2>
                <p>毎月・毎週開催される定期キャンペーンをチェック</p>
            </div>
            
            <div class="regular-campaign-list">
                <div class="regular-campaign-item">
                    <div class="regular-icon">🌙</div>
                    <div class="regular-content">
                        <h3>月末セール</h3>
                        <p>毎月末の3日間、対象商品が10〜15%OFF。在庫処分品は最大30%OFFになることも。</p>
                        <span class="regular-timing">開催：毎月28日〜31日</span>
                    </div>
                </div>
                
                <div class="regular-campaign-item">
                    <div class="regular-icon">⚡</div>
                    <div class="regular-content">
                        <h3>フラッシュセール</h3>
                        <p>不定期で開催される24時間限定のセール。メルマガ登録者に優先案内されます。</p>
                        <span class="regular-timing">開催：不定期（月1〜2回）</span>
                    </div>
                </div>
                
                <div class="regular-campaign-item">
                    <div class="regular-icon">🎂</div>
                    <div class="regular-content">
                        <h3>誕生日特典</h3>
                        <p>会員登録した方限定で、誕生月に使える10%OFFクーポンをプレゼント。</p>
                        <span class="regular-timing">開催：誕生月の1ヶ月間</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- 季節のキャンペーン予定 -->
        <section class="campaign-section mb-5">
            <div class="section-header text-center mb-4">
                <h2 class="section-title">🗓️ 今後のキャンペーン予定</h2>
                <p>見逃せない大型セールの予定をチェック</p>
            </div>
            
            <div class="timeline">
                <div class="timeline-item">
                    <div class="timeline-date">2月</div>
                    <div class="timeline-content">
                        <h3>バレンタインセール</h3>
                        <p>カップル向けモデルや、ペア購入で割引などのキャンペーンを予定。</p>
                    </div>
                </div>
                
                <div class="timeline-item">
                    <div class="timeline-date">3月</div>
                    <div class="timeline-content">
                        <h3>春の新生活応援セール</h3>
                        <p>新生活を始める方向けに、コンパクトモデルや軽量モデルがお得に。</p>
                    </div>
                </div>
                
                <div class="timeline-item">
                    <div class="timeline-date">5月</div>
                    <div class="timeline-content">
                        <h3>ゴールデンウィークセール</h3>
                        <p>年間最大級のセール。最大30%OFFや、送料無料キャンペーンを予定。</p>
                    </div>
                </div>
                
                <div class="timeline-item">
                    <div class="timeline-date">7月</div>
                    <div class="timeline-content">
                        <h3>夏のボーナスセール</h3>
                        <p>ハイエンドモデルやシリコン製モデルが特別価格に。</p>
                    </div>
                </div>
                
                <div class="timeline-item">
                    <div class="timeline-date">11月</div>
                    <div class="timeline-content">
                        <h3>ブラックフライデーセール</h3>
                        <p>年間最大の割引率。最大40%OFFのモデルも登場予定。</p>
                    </div>
                </div>
                
                <div class="timeline-item">
                    <div class="timeline-date">12月</div>
                    <div class="timeline-content">
                        <h3>年末大感謝祭</h3>
                        <p>1年の締めくくりに、全商品対象の大型セールを開催予定。</p>
                    </div>
                </div>
            </div>
        </section>

        <!-- お得に購入するコツ -->
        <section class="campaign-section mb-5">
            <div class="section-header text-center mb-4">
                <h2 class="section-title">💡 お得に購入するコツ</h2>
            </div>
            
            <div class="tips-grid">
                <div class="tip-card">
                    <div class="tip-icon">📧</div>
                    <h3>メルマガ登録</h3>
                    <p>各ショップのメルマガに登録すると、限定クーポンや先行セール情報が届きます。登録特典として初回10%OFFクーポンがもらえることも。</p>
                </div>
                
                <div class="tip-card">
                    <div class="tip-icon">🔔</div>
                    <h3>SNSをフォロー</h3>
                    <p>Twitter や Instagram で公式アカウントをフォローすると、フラッシュセールやタイムセールの情報をいち早くキャッチできます。</p>
                </div>
                
                <div class="tip-card">
                    <div class="tip-icon">🎟️</div>
                    <h3>クーポンを活用</h3>
                    <p>初回購入クーポン、誕生日クーポン、レビュー投稿クーポンなど、様々なクーポンを組み合わせてさらにお得に。</p>
                </div>
                
                <div class="tip-card">
                    <div class="tip-icon">📦</div>
                    <h3>まとめ買い</h3>
                    <p>アクセサリーやメンテナンスキットを同時購入すると、セット割引が適用されることがあります。</p>
                </div>
                
                <div class="tip-card">
                    <div class="tip-icon">⏰</div>
                    <h3>タイミングを見極める</h3>
                    <p>月末セールやボーナス時期、年末年始などの大型セール時期を狙うと、通常より大幅に安く購入できます。</p>
                </div>
                
                <div class="tip-card">
                    <div class="tip-icon">🔄</div>
                    <h3>アウトレット品をチェック</h3>
                    <p>展示品や旧モデルは、品質に問題なくても大幅割引されていることがあります。</p>
                </div>
            </div>
        </section>

        <!-- 注意事項 -->
        <section class="campaign-section mb-5">
            <div class="notice-box">
                <h3>⚠️ キャンペーン利用時の注意事項</h3>
                <ul>
                    <li>キャンペーンの内容や期間は予告なく変更される場合があります</li>
                    <li>複数のクーポンやキャンペーンの併用ができない場合があります</li>
                    <li>在庫状況により、キャンペーン対象商品が売り切れる場合があります</li>
                    <li>キャンペーン価格は各ショップの公式サイトで必ずご確認ください</li>
                    <li>返品・交換の条件はキャンペーン時も通常と同じです</li>
                </ul>
            </div>
        </section>

        <!-- CTA -->
        <section class="cta-box text-center mt-5">
            <h2 class="cta-box-title">お得なキャンペーンを活用して、理想のラブドールを手に入れよう</h2>
            <p class="cta-box-description">人気ランキングや販売店比較も参考にして、最適なタイミングで購入しましょう。</p>
            <div class="cta-buttons">
                <a href="<?php echo home_url('/#ranking'); ?>" class="btn btn-primary btn-lg">人気ランキングを見る</a>
                <a href="<?php echo home_url('/shop-comparison/'); ?>" class="btn btn-secondary btn-lg">販売店を比較する</a>
            </div>
        </section>

    </div><!-- .container -->

</main><!-- #main -->

<?php
get_footer();
