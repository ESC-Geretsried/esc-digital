(function () {
  if (!window.wp || !wp.blocks || !wp.element) return;
  wp.blocks.registerBlockType('esc-river-rats/next-home-game', {
    edit: function () { return wp.element.createElement('div', { className: 'esc-next-home-game-editor-placeholder' }, 'Nächstes Heimspiel (wird automatisch aus dem Spielplan ermittelt)'); },
    save: function () { return null; }
  });
}());
