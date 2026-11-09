const base = location.protocol === 'file:' ? 'guide.html' : '../brand.html';
location.replace(base + (location.hash || '#identity'));
