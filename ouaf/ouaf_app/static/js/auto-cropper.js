(function () {
  if (!window.Cropper) { console.warn('Cropper.js manquant'); return; }

  let cropper = null;
  let activeInput = null;
  let scopeEl = null;
  let outW = 1600, outH = 900;

  function ensureModal() {
    let dlg = document.getElementById('cropperModal');
    if (dlg) return dlg;

    dlg = document.createElement('dialog');
    dlg.id = 'cropperModal';
    dlg.style.cssText = 'max-width:900px;width:clamp(320px,90vw,900px);border:1px solid #f3a9a0;border-radius:10px;padding:0;';
    dlg.innerHTML = `
      <div class="account__card" style="margin:0;border:none;box-shadow:none;">
        <header class="account__head">
          <h2 class="account__title" style="margin:0;">Recadrer l’image</h2>
          <p class="account__meta">Zoomez/déplacez puis validez.</p>
        </header>
        <div class="account__body">
          <div style="max-height:65vh;overflow:auto;">
            <img id="cropperTarget" alt="Aperçu à recadrer" style="max-width:100%;display:block;">
          </div>
          <footer class="account__foot">
            <button type="button" class="btn btn--ghost" data-close>Annuler</button>
            <button type="button" class="btn btn--primary" id="cropperConfirm">Valider</button>
          </footer>
        </div>
      </div>`;
    document.body.appendChild(dlg);

    // Events modal
    dlg.addEventListener('click', (e) => {
      if (e.target.hasAttribute('data-close')) {
        closeModal();
      }
    });
    dlg.querySelector('#cropperConfirm').addEventListener('click', onConfirm);
    return dlg;
  }

  function openFor(input) {
    const file = input.files && input.files[0];
    if (!file || !/^image\//.test(file.type)) return;

    activeInput = input;
    scopeEl = input.closest('.js-crop-scope') || input.parentElement;

    const aspectStr = (scopeEl?.dataset.cropAspect || input.dataset.cropAspect || '16/9').trim();
    const sizeStr   = (scopeEl?.dataset.cropSize   || input.dataset.cropSize   || '1600x900').trim();

    const [aw, ah] = aspectStr.split('/').map(Number);
    const [sw, sh] = sizeStr.split('x').map(Number);
    const ratio = (aw > 0 && ah > 0) ? aw/ah : 16/9;
    outW = sw > 0 ? sw : 1600;
    outH = sh > 0 ? sh : 900;

    const dlg = ensureModal();
    const img = dlg.querySelector('#cropperTarget');
    const url = URL.createObjectURL(file);
    img.src = url;

    img.onload = () => {
      if (cropper) { cropper.destroy(); cropper = null; }
      cropper = new Cropper(img, {
        aspectRatio: ratio,
        viewMode: 1,
        autoCropArea: 1,
        background: false,
        movable: true,
        zoomable: true,
      });
    };

    if (typeof dlg.showModal === 'function') dlg.showModal();
    else dlg.setAttribute('open', 'open');
  }

  function closeModal() {
    const dlg = document.getElementById('cropperModal');
    if (!dlg) return;
    if (dlg.close) dlg.close(); else dlg.removeAttribute('open');
    if (cropper) { cropper.destroy(); cropper = null; }
    activeInput = null;
    scopeEl = null;
  }

  function onConfirm() {
    if (!cropper || !activeInput) return;

    const srcType = (activeInput.files[0]?.type || '').toLowerCase();
    const mime = srcType.includes('png') ? 'image/png' : 'image/jpeg';
    const quality = mime === 'image/jpeg' ? 0.92 : 0.96;

    const canvas = cropper.getCroppedCanvas({ width: outW, height: outH });
    canvas.toBlob((blob) => {
      if (!blob) return;
      const orig = activeInput.files[0];
      const base = (orig?.name?.replace(/\.[^.]+$/, '') || 'image');
      const ext = (mime === 'image/png') ? 'png' : 'jpg';
      const cropped = new File([blob], `${base}-cropped.${ext}`, { type: mime });

      const dt = new DataTransfer();
      dt.items.add(cropped);
      activeInput.files = dt.files;

      const preview = scopeEl?.querySelector('.media_form__preview_content');
      if (preview) {
        preview.src = URL.createObjectURL(cropped);
        preview.style.display = '';
      }

      closeModal();
    }, mime, quality);
  }


  document.addEventListener('change', (e) => {
    const input = e.target.closest('input[type="file"]');
    if (!input) return;
    const scope = input.closest('.js-crop-scope');
    if (!scope) return;
    if (!input.accept) input.setAttribute('accept', 'image/*');
    if (input.files && input.files[0]) openFor(input);
  });
})();
