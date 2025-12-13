/**
 * アフィリエイトリンク自動変換スクリプト
 * 
 * プラグインが出力したリンクを自動的にアフィリエイトリンクに変換します
 */

(function() {
    'use strict';

    // WordPress から設定を取得（wp_localize_script で渡される）
    const affiliateSettings = window.lovedollAffiliateSettings || { links: [] };

    /**
     * URLをアフィリエイトリンクに変換
     */
    function convertToAffiliateLink(url) {
        if (!url) return url;

        // 有効な設定のみを対象
        const activeLinks = affiliateSettings.links.filter(link => link.enabled);

        for (let i = 0; i < activeLinks.length; i++) {
            const link = activeLinks[i];
            
            // ドメインが一致するかチェック
            if (url.includes(link.domain)) {
                try {
                    const urlObj = new URL(url);
                    
                    // パラメータを解析
                    const param = link.param.replace(/^\?/, ''); // 先頭の ? を削除
                    const paramPairs = param.split('&');
                    
                    // 各パラメータを追加
                    paramPairs.forEach(pair => {
                        const [key, value] = pair.split('=');
                        if (key && value) {
                            // 既存のパラメータを上書きしない
                            if (!urlObj.searchParams.has(key)) {
                                urlObj.searchParams.set(key, value);
                            }
                        }
                    });
                    
                    return urlObj.toString();
                } catch (e) {
                    console.warn('URL parsing error:', e);
                    return url;
                }
            }
        }

        return url;
    }

    /**
     * ページ内のすべてのリンクを変換
     */
    function convertAllLinks() {
        // すべての a タグを取得
        const links = document.querySelectorAll('a[href]');
        let convertedCount = 0;

        links.forEach(link => {
            const originalHref = link.getAttribute('href');
            
            // 外部リンクのみを対象（http または https で始まる）
            if (originalHref && (originalHref.startsWith('http://') || originalHref.startsWith('https://'))) {
                const convertedHref = convertToAffiliateLink(originalHref);
                
                if (convertedHref !== originalHref) {
                    link.setAttribute('href', convertedHref);
                    link.setAttribute('data-original-href', originalHref);
                    link.setAttribute('data-affiliate-converted', 'true');
                    convertedCount++;
                }
            }
        });

        if (convertedCount > 0) {
            console.log(`[Affiliate Link Converter] ${convertedCount} links converted`);
        }
    }

    /**
     * 動的に追加されたリンクを監視
     */
    function observeDynamicLinks() {
        // MutationObserver で DOM の変更を監視
        const observer = new MutationObserver(function(mutations) {
            let shouldConvert = false;

            mutations.forEach(function(mutation) {
                // 新しいノードが追加された場合
                if (mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach(function(node) {
                        // a タグまたは a タグを含む要素が追加された場合
                        if (node.nodeType === 1) { // Element node
                            if (node.tagName === 'A' || node.querySelector('a')) {
                                shouldConvert = true;
                            }
                        }
                    });
                }
            });

            if (shouldConvert) {
                // 少し遅延させて変換（プラグインの処理完了を待つ）
                setTimeout(convertAllLinks, 100);
            }
        });

        // body 全体を監視
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    /**
     * 初期化
     */
    function init() {
        // 設定が存在しない場合は何もしない
        if (!affiliateSettings.links || affiliateSettings.links.length === 0) {
            console.log('[Affiliate Link Converter] No affiliate settings found');
            return;
        }

        console.log('[Affiliate Link Converter] Initialized with', affiliateSettings.links.length, 'sites');

        // 初回変換
        convertAllLinks();

        // 動的リンクの監視を開始
        observeDynamicLinks();

        // ページ読み込み完了後にもう一度変換（プラグインの遅延読み込み対策）
        window.addEventListener('load', function() {
            setTimeout(convertAllLinks, 500);
        });

        // Ajax 完了後にも変換（WordPress の Ajax 対応）
        if (typeof jQuery !== 'undefined') {
            jQuery(document).ajaxComplete(function() {
                setTimeout(convertAllLinks, 100);
            });
        }
    }

    // DOM 読み込み完了後に初期化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
