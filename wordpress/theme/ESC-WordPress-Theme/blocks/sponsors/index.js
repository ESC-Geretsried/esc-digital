(function () {
  if (!window.wp || !wp.blocks || !wp.element) return;
  wp.blocks.registerBlockType('esc-river-rats/sponsors', {
    edit: function () {
      return wp.element.createElement('div', { className: 'esc-sponsors-editor-placeholder' }, 'Sponsorenband (wird automatisch ausgegeben)');
    },
    save: function () { return null; }
  });
}());
