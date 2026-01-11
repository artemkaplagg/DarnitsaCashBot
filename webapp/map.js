let map;
let currentMarker = null;
const tg = window.Telegram.WebApp;

const EXCHANGERS_DATA = [
    {
        id: 1,
        name: "Обмінник Позняки",
        address: "просп. Петра Григоренка, 28, Київ",
        district: "Позняки",
        phone: "+380 (50) 388-88-65",
        lat: 50.4165,
        lon: 30.6327,
        rates: {
            USD: { buy: null, sell: null, updated: null },
            EUR: { buy: null, sell: null, updated: null }
        }
    },
    {
        id: 2,
        name: "Money Exchange Kyiv",
        address: "вул. Ревуцького, 12/1, Київ",
        district: "Осокорки/Позняки",
        phone: "",
        lat: 50.4189,
        lon: 30.6145,
        rates: {
            USD: { buy: null, sell: null, updated: null },
            EUR: { buy: null, sell: null, updated: null }
        }
    },
    {
        id: 3,
        name: "Обмін Валют GARANT",
        address: "Харківське шосе, 144В, Київ",
        district: "Харківський масив",
        phone: "",
        lat: 50.4012,
        lon: 30.6589,
        rates: {
            USD: { buy: null, sell: null, updated: null },
            EUR: { buy: null, sell: null, updated: null }
        }
    },
    {
        id: 4,
        name: "Обмін валют",
        address: "вул. Ялтинська, 6, Київ",
        district: "Дарниця",
        phone: "",
        lat: 50.4453,
        lon: 30.6234,
        rates: {
            USD: { buy: null, sell: null, updated: null },
            EUR: { buy: null, sell: null, updated: null }
        }
    },
    {
        id: 5,
        name: "Obmin Valyut",
        address: "вул. Срібнокільська, 1-А, Київ",
        district: "Осокорки/Позняки",
        phone: "",
        lat: 50.4001,
        lon: 30.6178,
        rates: {
            USD: { buy: null, sell: null, updated: null },
            EUR: { buy: null, sell: null, updated: null }
        }
    },
    {
        id: 6,
        name: "Obmen Vsekh Valyut",
        address: "вул. Срібнокільська, 3Д, Київ",
        district: "Осокорки/Позняки",
        phone: "",
        lat: 50.3998,
        lon: 30.6201,
        rates: {
            USD: { buy: null, sell: null, updated: null },
            EUR: { buy: null, sell: null, updated: null }
        }
    },
    {
        id: 7,
        name: "Obmin Valyut",
        address: "вул. Олени Пчілки, 2, Київ",
        district: "Дарницький",
        phone: "",
        lat: 50.4389,
        lon: 30.6123,
        rates: {
            USD: { buy: null, sell: null, updated: null },
            EUR: { buy: null, sell: null, updated: null }
        }
    },
    {
        id: 8,
        name: "Обмін валют",
        address: "просп. Миколи Бажана, 26, Київ",
        district: "Осокорки/Позняки",
        phone: "",
        lat: 50.4234,
        lon: 30.6412,
        rates: {
            USD: { buy: null, sell: null, updated: null },
            EUR: { buy: null, sell: null, updated: null }
        }
    },
    {
        id: 9,
        name: "Money Exchange Kyiv",
        address: "Дніпровська площа, 1, Київ",
        district: "Дарницький",
        phone: "",
        lat: 50.4512,
        lon: 30.6289,
        rates: {
            USD: { buy: null, sell: null, updated: null },
            EUR: { buy: null, sell: null, updated: null }
        }
    },
    {
        id: 10,
        name: "Obmin Valyut",
        address: "вул. Михайла Драгоманова, 2, Київ",
        district: "Позняки/Харківський масив",
        phone: "",
        lat: 50.4089,
        lon: 30.6534,
        rates: {
            USD: { buy: null, sell: null, updated: null },
            EUR: { buy: null, sell: null, updated: null }
        }
    }
];

function initMap() {
    tg.ready();
    tg.expand();
    
    const center = [50.4200, 30.6300];
    
    map = L.map('map', {
        zoomControl: true,
        attributionControl: false
    }).setView(center, 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
    }).addTo(map);
    
    EXCHANGERS_DATA.forEach(exchanger => {
        addMarker(exchanger);
    });
    
    document.getElementById('loading').style.display = 'none';
    
    document.getElementById('close-info').addEventListener('click', closeInfoPanel);
}

function addMarker(exchanger) {
    const customIcon = L.divIcon({
        className: 'custom-marker',
        html: `
            <div class="marker-pin">
                <span class="marker-icon">💱</span>
            </div>
        `,
        iconSize: [40, 40],
        iconAnchor: [20, 40],
        popupAnchor: [0, -40]
    });
    
    const marker = L.marker([exchanger.lat, exchanger.lon], {
        icon: customIcon
    }).addTo(map);
    
    const popupContent = `
        <div class="popup-content">
            <div class="popup-title">${exchanger.name}</div>
            <div class="popup-address">📍 ${exchanger.address}</div>
            <div class="popup-district">📌 ${exchanger.district}</div>
            <button class="popup-btn" onclick="showExchangerInfo(${exchanger.id})">
                Детальніше
            </button>
        </div>
    `;
    
    marker.bindPopup(popupContent);
    
    marker.on('click', () => {
        currentMarker = exchanger;
    });
}

function showExchangerInfo(exchangerId) {
    const exchanger = EXCHANGERS_DATA.find(ex => ex.id === exchangerId);
    if (!exchanger) return;
    
    document.getElementById('info-title').textContent = exchanger.name;
    document.getElementById('info-address').textContent = exchanger.address;
    document.getElementById('info-district').textContent = exchanger.district;
    
    if (exchanger.phone) {
        document.getElementById('phone-row').style.display = 'flex';
        const phoneLink = document.getElementById('info-phone');
        phoneLink.textContent = exchanger.phone;
        phoneLink.href = `tel:${exchanger.phone.replace(/\s/g, '')}`;
    } else {
        document.getElementById('phone-row').style.display = 'none';
    }
    
    const hasUSD = exchanger.rates.USD.buy !== null;
    const hasEUR = exchanger.rates.EUR.buy !== null;
    
    if (hasUSD) {
        document.getElementById('usd-rate').style.display = 'block';
        document.getElementById('usd-buy').textContent = exchanger.rates.USD.buy.toFixed(2) + ' ₴';
        document.getElementById('usd-sell').textContent = exchanger.rates.USD.sell.toFixed(2) + ' ₴';
        
        if (exchanger.rates.USD.updated) {
            const updateTime = formatUpdateTime(exchanger.rates.USD.updated);
            document.getElementById('usd-updated').textContent = `Оновлено: ${updateTime}`;
        }
    } else {
        document.getElementById('usd-rate').style.display = 'none';
    }
    
    if (hasEUR) {
        document.getElementById('eur-rate').style.display = 'block';
        document.getElementById('eur-buy').textContent = exchanger.rates.EUR.buy.toFixed(2) + ' ₴';
        document.getElementById('eur-sell').textContent = exchanger.rates.EUR.sell.toFixed(2) + ' ₴';
        
        if (exchanger.rates.EUR.updated) {
            const updateTime = formatUpdateTime(exchanger.rates.EUR.updated);
            document.getElementById('eur-updated').textContent = `Оновлено: ${updateTime}`;
        }
    } else {
        document.getElementById('eur-rate').style.display = 'none';
    }
    
    if (!hasUSD && !hasEUR) {
        document.getElementById('no-rates').style.display = 'block';
    } else {
        document.getElementById('no-rates').style.display = 'none';
    }
    
    const navigateBtn = document.getElementById('navigate-btn');
    navigateBtn.onclick = () => {
        const url = `https://www.google.com/maps/dir/?api=1&destination=${exchanger.lat},${exchanger.lon}`;
        window.open(url, '_blank');
    };
    
    document.getElementById('info-panel').classList.remove('hidden');
    
    map.setView([exchanger.lat, exchanger.lon], 16);
}

function closeInfoPanel() {
    document.getElementById('info-panel').classList.add('hidden');
}

function formatUpdateTime(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMinutes = Math.floor((now - date) / 60000);
    
    if (diffMinutes < 1) return 'щойно';
    if (diffMinutes < 60) return `${diffMinutes} хв тому`;
    
    const diffHours = Math.floor(diffMinutes / 60);
    if (diffHours < 24) return `${diffHours} год тому`;
    
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    
    return `${day}.${month} о ${hours}:${minutes}`;
}

document.addEventListener('DOMContentLoaded', initMap);

