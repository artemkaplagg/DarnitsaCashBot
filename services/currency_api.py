import aiohttp
from typing import Dict, Optional
from datetime import datetime
import pytz


class CurrencyAPI:
    def __init__(self):
        self.nbu_url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
        self.mono_url = "https://api.monobank.ua/bank/currency"
        self.privat_url = "https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5"
        
        self.cache = {}
        self.cache_timeout = 300  # 5 минут
    
    async def _fetch(self, url: str) -> Optional[Dict]:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        return await response.json()
        except Exception as e:
            print(f"Ошибка при запросе {url}: {e}")
        return None
    
    async def get_nbu_rates(self) -> Dict[str, float]:
        """Получить официальные курсы НБУ"""
        data = await self._fetch(self.nbu_url)
        
        rates = {}
        if data:
            for item in data:
                if item.get('cc') in ['USD', 'EUR']:
                    rates[item['cc']] = {
                        'rate': round(item.get('rate', 0), 2),
                        'source': 'nbu'
                    }
        
        return rates
    
    async def get_mono_rates(self) -> Dict[str, Dict]:
        """Получить курсы Monobank"""
        data = await self._fetch(self.mono_url)
        
        rates = {}
        if data:
            # Коды валют: 840 = USD, 978 = EUR, 980 = UAH
            currency_codes = {840: 'USD', 978: 'EUR'}
            
            for item in data:
                currency_code = item.get('currencyCodeA')
                base_code = item.get('currencyCodeB')
                
                if currency_code in currency_codes and base_code == 980:
                    currency = currency_codes[currency_code]
                    rates[currency] = {
                        'buy': round(item.get('rateBuy', 0), 2),
                        'sell': round(item.get('rateSell', 0), 2),
                        'source': 'monobank'
                    }
        
        return rates
    
    async def get_privat_rates(self) -> Dict[str, Dict]:
        """Получить курсы PrivatBank"""
        data = await self._fetch(self.privat_url)
        
        rates = {}
        if data:
            for item in data:
                currency = item.get('ccy')
                if currency in ['USD', 'EUR']:
                    rates[currency] = {
                        'buy': round(float(item.get('buy', 0)), 2),
                        'sell': round(float(item.get('sale', 0)), 2),
                        'source': 'privatbank'
                    }
        
        return rates
    
    async def get_all_rates(self) -> Dict:
        """Получить все курсы одновременно"""
        nbu = await self.get_nbu_rates()
        mono = await self.get_mono_rates()
        privat = await self.get_privat_rates()
        
        kyiv_tz = pytz.timezone('Europe/Kiev')
        current_time = datetime.now(kyiv_tz).strftime('%H:%M')
        
        result = {
            'timestamp': current_time,
            'USD': {
                'nbu': nbu.get('USD', {}).get('rate'),
                'monobank': mono.get('USD', {}),
                'privatbank': privat.get('USD', {})
            },
            'EUR': {
                'nbu': nbu.get('EUR', {}).get('rate'),
                'monobank': mono.get('EUR', {}),
                'privatbank': privat.get('EUR', {})
            }
        }
        
        return result
    
    def calculate_change(self, current: float, previous: float) -> tuple:
        """Расчет изменения курса (разница и процент)"""
        if not previous or previous == 0:
            return 0, 0
        
        diff = round(current - previous, 2)
        percent = round((diff / previous) * 100, 2)
        
        return diff, percent
    
    def get_trend_emoji(self, diff: float) -> str:
        """Получить эмодзи тренда"""
        if diff > 0:
            return "📈"
        elif diff < 0:
            return "📉"
        else:
            return "➡️"


# Глобальный экземпляр
currency_api = CurrencyAPI()

