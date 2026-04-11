(function () {
  'use strict';

  if (!location.pathname.match(/\/admin\/products\/category\//)) return;

  document.addEventListener('DOMContentLoaded', function () {
    var bar = document.createElement('div');
    bar.id = 'sort-save-bar';
    bar.innerHTML =
      '<span>順序已變更</span>' +
      '<button id="sort-save-btn">儲存排序</button>' +
      '<span id="sort-save-msg"></span>';
    document.body.appendChild(bar);

    document.addEventListener('click', function (e) {
      if (e.target && e.target.id === 'sort-save-btn') { saveOrder(); return; }

      var indentBtn  = e.target && e.target.closest('.indent-btn');
      var outdentBtn = e.target && e.target.closest('.outdent-btn');
      if (indentBtn)  { e.stopPropagation(); e.preventDefault(); handleIndent(indentBtn); }
      if (outdentBtn) { e.stopPropagation(); e.preventDefault(); handleOutdent(outdentBtn); }
    }, true); // capture phase — intercept before link navigation

    setTimeout(init, 200);
  });

  function init() {
    var table = document.querySelector('#result_list');
    if (!table) { setTimeout(init, 300); return; }
    if (typeof Sortable === 'undefined') { setTimeout(init, 100); return; }

    Sortable.create(table, {
      handle: '.drag-handle',
      draggable: 'tbody',
      animation: 150,
      ghostClass: 'sortable-ghost',
      chosenClass: 'sortable-chosen',
      onEnd: function () {
        updateVisibility();
        document.getElementById('sort-save-bar').classList.add('visible');
        document.getElementById('sort-save-msg').textContent = '';
      },
    });

    updateVisibility();
  }

  // → indent: one level at a time
  function handleIndent(btn) {
    var controls = btn.closest('.cat-row-controls');
    var id = parseInt(controls.dataset.id, 10);
    var tbody = controls.closest('tbody');
    var prevTbody = prevSiblingTbody(tbody);
    if (!prevTbody) return;
    var prevControls = prevTbody.querySelector('.cat-row-controls');
    if (!prevControls) return;

    var prevParentId = prevControls.dataset.parentId || null;
    var newParentId, parentName;
    if (!prevParentId) {
      // row above is top-level → become its child
      newParentId = parseInt(prevControls.dataset.id, 10);
      parentName = getNameFromTbody(prevTbody);
    } else {
      // row above is already a child → align same level (same parent)
      newParentId = parseInt(prevParentId, 10);
      var parentTbody = findTbodyById(String(newParentId));
      parentName = parentTbody ? getNameFromTbody(parentTbody) : '';
    }

    controls.dataset.parentId = String(newParentId);
    setParentCell(tbody, parentName);
    updateVisibility();
    saveParentAndOrder(id, newParentId);
  }

  // ← outdent: remove parent, move row to after the last sibling
  function handleOutdent(btn) {
    var controls = btn.closest('.cat-row-controls');
    var id = parseInt(controls.dataset.id, 10);
    var tbody = controls.closest('tbody');
    var formerParentId = controls.dataset.parentId;

    var allTbodies = Array.from(document.querySelectorAll('#result_list tbody'));
    var lastSibling = null;
    allTbodies.forEach(function (tb) {
      if (tb === tbody) return;
      var c = tb.querySelector('.cat-row-controls');
      if (c && c.dataset.parentId === formerParentId) lastSibling = tb;
    });

    var anchor = lastSibling;
    if (!anchor) {
      allTbodies.forEach(function (tb) {
        var c = tb.querySelector('.cat-row-controls');
        if (c && c.dataset.id === formerParentId) anchor = tb;
      });
    }
    if (anchor && anchor.nextSibling !== tbody) {
      anchor.parentNode.insertBefore(tbody, anchor.nextSibling);
    }

    controls.dataset.parentId = '';
    setParentCell(tbody, null);
    updateVisibility();
    saveParentAndOrder(id, null);
  }

  // find a tbody by its category id
  function findTbodyById(id) {
    var all = document.querySelectorAll('#result_list tbody');
    for (var i = 0; i < all.length; i++) {
      var c = all[i].querySelector('.cat-row-controls');
      if (c && c.dataset.id === id) return all[i];
    }
    return null;
  }

  // get category name text from a tbody row
  function getNameFromTbody(tbody) {
    // list_display: drag_handle(0), name(1), ...
    // find td by data-label or fall back to index 1
    var td = findCellByLabel(tbody, 'name') || tbody.querySelectorAll('tr:first-child td')[1];
    return td ? td.textContent.trim() : '';
  }

  // update the "parent" column cell content
  function setParentCell(tbody, parentName) {
    var td = findCellByLabel(tbody, 'parent') || tbody.querySelectorAll('tr:first-child td')[3];
    if (!td) return;
    // preserve the existing wrapper div if present, else just set text
    var inner = td.querySelector('div') || td;
    inner.textContent = parentName || '-';
  }

  function findCellByLabel(tbody, label) {
    var tds = tbody.querySelectorAll('tr:first-child td');
    for (var i = 0; i < tds.length; i++) {
      var l = (tds[i].getAttribute('data-label') || '').toLowerCase();
      if (l === label) return tds[i];
    }
    return null;
  }

  function updateVisibility() {
    var tbodies = document.querySelectorAll('#result_list tbody');
    tbodies.forEach(function (tbody, idx) {
      var controls = tbody.querySelector('.cat-row-controls');
      if (!controls) return;
      var hasParent   = !!controls.dataset.parentId;
      var hasChildren = controls.dataset.hasChildren === '1';
      var isFirst     = idx === 0;

      var indentBtn  = controls.querySelector('.indent-btn');
      var outdentBtn = controls.querySelector('.outdent-btn');

      // visual row indent
      if (hasParent) {
        tbody.classList.add('cat-child-row');
      } else {
        tbody.classList.remove('cat-child-row');
      }

      if (hasParent) {
        indentBtn.style.display  = 'none';
        outdentBtn.style.display = 'inline-flex';
      } else if (hasChildren) {
        indentBtn.style.display  = 'none';
        outdentBtn.style.display = 'none';
      } else {
        indentBtn.style.display  = isFirst ? 'none' : 'inline-flex';
        outdentBtn.style.display = 'none';
      }
    });
  }

  function prevSiblingTbody(tbody) {
    var prev = tbody.previousElementSibling;
    while (prev && prev.tagName !== 'TBODY') prev = prev.previousElementSibling;
    return prev || null;
  }

  function saveParentAndOrder(id, parentId) {
    var base = location.pathname.replace(/\/$/, '');
    var csrfToken = getCookie('csrftoken');

    var orderPayload = [];
    document.querySelectorAll('#result_list .cat-row-controls').forEach(function (el, i) {
      var elId = parseInt(el.dataset.id, 10);
      if (elId) orderPayload.push({ id: elId, order: i });
    });

    fetch(base + '/reorder/save/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
      body: JSON.stringify(orderPayload),
    })
      .then(function () {
        return fetch(base + '/parent/save/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
          body: JSON.stringify({ id: id, parent_id: parentId }),
        });
      })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data.ok) alert('錯誤：' + data.error);
      })
      .catch(function () { alert('網路錯誤'); });
  }

  function saveOrder() {
    var handles = document.querySelectorAll('#result_list .cat-row-controls');
    var payload = [];
    handles.forEach(function (el, i) {
      var id = parseInt(el.dataset.id, 10);
      if (id) payload.push({ id: id, order: i });
    });

    var btn = document.getElementById('sort-save-btn');
    var msg = document.getElementById('sort-save-msg');
    btn.disabled = true;
    msg.style.color = '#fff';
    msg.textContent = '儲存中…';

    var base = location.pathname.replace(/\/$/, '');
    fetch(base + '/reorder/save/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify(payload),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.ok) {
          msg.textContent = '✓ 已儲存';
          msg.style.color = '#4ade80';
          setTimeout(function () {
            document.getElementById('sort-save-bar').classList.remove('visible');
          }, 1500);
        } else {
          msg.textContent = '錯誤：' + data.error;
          msg.style.color = '#f87171';
        }
        btn.disabled = false;
      })
      .catch(function () {
        msg.textContent = '網路錯誤';
        msg.style.color = '#f87171';
        btn.disabled = false;
      });
  }

  function getCookie(name) {
    var v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
    return v ? v[2] : '';
  }
})();
