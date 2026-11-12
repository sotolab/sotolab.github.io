const hash = location.hash;
const isLegacyBrand = location.pathname.endsWith('/brand.html');
const kitSections = ['#identity', '#logo-variants', '#brand-kit', '#colors', '#type', '#voice', '#applications', '#downloads'];
const kitHash = ['#logo-variants', '#brand-kit'].includes(hash) ? '#identity' : hash;

if (!isLegacyBrand) {
  location.replace('guide.html' + kitHash);
} else if (kitSections.includes(hash)) {
  location.replace('brand-kit/guide.html' + kitHash);
} else {
  location.replace('index.html#brand');
}
