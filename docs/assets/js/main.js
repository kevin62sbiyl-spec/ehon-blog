// 目次ハイライト
const headings = document.querySelectorAll('.article-content h2, .article-content h3');
const tocLinks = document.querySelectorAll('.toc a');
if (headings.length && tocLinks.length) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        tocLinks.forEach(l => l.style.color = '');
        const link = document.querySelector(`.toc a[href="#${e.target.id}"]`);
        if (link) link.style.color = '#c84b2f';
      }
    });
  }, { rootMargin: '-20% 0% -70% 0%' });
  headings.forEach(h => { if (h.id) observer.observe(h); });
}

// スクロールトップ
const scrollBtn = document.createElement('button');
scrollBtn.textContent = '↑';
scrollBtn.style.cssText = 'position:fixed;bottom:24px;right:24px;width:44px;height:44px;border-radius:50%;background:#1a1814;color:#fff;border:none;font-size:18px;cursor:pointer;opacity:0;transition:opacity .3s;z-index:999';
document.body.appendChild(scrollBtn);
window.addEventListener('scroll', () => {
  scrollBtn.style.opacity = window.scrollY > 400 ? '1' : '0';
});
scrollBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
