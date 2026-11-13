const isLegacyBrand = location.pathname.endsWith('/brand.html');
const kitSections = ['#identity', '#logo-variants', '#brand-kit', '#colors', '#type', '#voice', '#applications', '#downloads'];

function openKit() {
  const hash = location.hash;
  const kitHash = ['#logo-variants', '#brand-kit'].includes(hash) ? '#identity' : hash;
  if (!isLegacyBrand || kitSections.includes(hash)) {
    location.replace((isLegacyBrand ? 'brand-kit/guide.html' : 'guide.html') + kitHash);
  }
}

openKit();
if (isLegacyBrand) window.addEventListener('hashchange', openKit);
