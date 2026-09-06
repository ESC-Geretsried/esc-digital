(function () {
  if (!window.wp || !wp.blocks || !wp.element) return;
  wp.blocks.registerBlockType('esc-river-rats/flash-news', {
    edit: function () {
      return wp.element.createElement('div', { className: 'esc-flashnews-editor-placeholder' }, 'Flash-News-Leiste (wird automatisch ausgegeben)');
    },
    save: function () { return null; }
  });
}());
