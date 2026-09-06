(function () {
	'use strict';
	function toggleMobileMenu(button, open) {
		var nav = document.getElementById('esc-main-nav');
		if (!nav) { return; }
		var expanded = typeof open === 'boolean' ? open : !nav.classList.contains('is-mobile-open');
		nav.classList.toggle('is-mobile-open', expanded);
		button.setAttribute('aria-expanded', expanded ? 'true' : 'false');
		button.setAttribute('aria-label', expanded ? 'Menü schließen' : 'Menü öffnen');
	}
	function closeMenus() {
		document.querySelectorAll('.esc-main-nav .menu-item-has-children.is-open').forEach(function (item) {
			item.classList.remove('is-open');
			var link = item.querySelector(':scope > a');
			if (link) { link.setAttribute('aria-expanded', 'false'); }
		});
	}
	document.addEventListener('click', function (event) {
		var mobileToggle = event.target.closest('.esc-mobile-menu-toggle');
		if (mobileToggle) { toggleMobileMenu(mobileToggle); return; }
		var link = event.target.closest('.esc-main-nav .menu-item-has-children > a');
		if (link) {
			var item = link.parentElement;
			if (!item.classList.contains('is-open')) {
				event.preventDefault();
				closeMenus();
				item.classList.add('is-open');
				link.setAttribute('aria-expanded', 'true');
			}
			return;
		}
		if (!event.target.closest('.esc-main-nav') && !event.target.closest('.esc-mobile-menu-toggle')) {
			closeMenus();
			var button = document.querySelector('.esc-mobile-menu-toggle');
			if (button) { toggleMobileMenu(button, false); }
		}
	});
	document.addEventListener('keydown', function (event) {
		if (event.key === 'Escape') { closeMenus(); var button = document.querySelector('.esc-mobile-menu-toggle'); if (button) { toggleMobileMenu(button, false); } }
	});
}());
