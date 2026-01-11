import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from config import DATA_DIR


class Storage:
    def __init__(self):
        # Создаём папку data если её нет
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        self.exchangers_file = os.path.join(DATA_DIR, 'exchangers.json')
        self.rates_history_file = os.path.join(DATA_DIR, 'rates_history.json')
        self.user_alerts_file = os.path.join(DATA_DIR, 'user_alerts.json')
        self.user_settings_file = os.path.join(DATA_DIR, 'user_settings.json')
        
        # Инициализируем файлы если их нет
        self._init_files()
    
    def _init_files(self):
        # Инициализация exchangers.json
        if not os.path.exists(self.exchangers_file):
            initial_exchangers = [
                {
                    "id": 1,
                    "name": "Обмінник Позняки",
                    "address": "просп. Петра Григоренка, 28, Київ",
                    "district": "Позняки",
                    "phone": "+380 (50) 388-88-65",
                    "lat": 50.4165,
                    "lon": 30.6327,
                    "rates": {
                        "USD": {"buy": None, "sell": None, "updated": None},
                        "EUR": {"buy": None, "sell": None, "updated": None}
                    }
                },
                {
                    "id": 2,
                    "name": "Money Exchange Kyiv",
                    "address": "вул. Ревуцького, 12/1, Київ",
                    "district": "Осокорки/Позняки",
                    "phone": "",
                    "lat": 50.4189,
                    "lon": 30.6145,
                    "rates": {
                        "USD": {"buy": None, "sell": None, "updated": None},
                        "EUR": {"buy": None, "sell": None, "updated": None}
                    }
                },
                {
                    "id": 3,
                    "name": "Обмін Валют GARANT",
                    "address": "Харківське шосе, 144В, Київ",
                    "district": "Харківський масив",
                    "phone": "",
                    "lat": 50.4012,
                    "lon": 30.6589,
                    "rates": {
                        "USD": {"buy": None, "sell": None, "updated": None},
                        "EUR": {"buy": None, "sell": None, "updated": None}
                    }
                },
                {
                    "id": 4,
                    "name": "Обмін валют",
                    "address": "вул. Ялтинська, 6, Київ",
                    "district": "Дарниця",
                    "phone": "",
                    "lat": 50.4453,
                    "lon": 30.6234,
                    "rates": {
                        "USD": {"buy": None, "sell": None, "updated": None},
                        "EUR": {"buy": None, "sell": None, "updated": None}
                    }
                },
                {
                    "id": 5,
                    "name": "Obmin Valyut",
                    "address": "вул. Срібнокільська, 1-А, Київ",
                    "district": "Осокорки/Позняки",
                    "phone": "",
                    "lat": 50.4001,
                    "lon": 30.6178,
                    "rates": {
                        "USD": {"buy": None, "sell": None, "updated": None},
                        "EUR": {"buy": None, "sell": None, "updated": None}
                    }
                },
                {
                    "id": 6,
                    "name": "Obmen Vsekh Valyut",
                    "address": "вул. Срібнокільська, 3Д, Київ",
                    "district": "Осокорки/Позняки",
                    "phone": "",
                    "lat": 50.3998,
                    "lon": 30.6201,
                    "rates": {
                        "USD": {"buy": None, "sell": None, "updated": None},
                        "EUR": {"buy": None, "sell": None, "updated": None}
                    }
                },
                {
                    "id": 7,
                    "name": "Obmin Valyut",
                    "address": "вул. Олени Пчілки, 2, Київ",
                    "district": "Дарницький",
                    "phone": "",
                    "lat": 50.4389,
                    "lon": 30.6123,
                    "rates": {
                        "USD": {"buy": None, "sell": None, "updated": None},
                        "EUR": {"buy": None, "sell": None, "updated": None}
                    }
                },
                {
                    "id": 8,
                    "name": "Обмін валют",
                    "address": "просп. Миколи Бажана, 26, Київ",
                    "district": "Осокорки/Позняки",
                    "phone": "",
                    "lat": 50.4234,
                    "lon": 30.6412,
                    "rates": {
                        "USD": {"buy": None, "sell": None, "updated": None},
                        "EUR": {"buy": None, "sell": None, "updated": None}
                    }
                },
                {
                    "id": 9,
                    "name": "Money Exchange Kyiv",
                    "address": "Дніпровська площа, 1, Київ",
                    "district": "Дарницький",
                    "phone": "",
                    "lat": 50.4512,
                    "lon": 30.6289,
                    "rates": {
                        "USD": {"buy": None, "sell": None, "updated": None},
                        "EUR": {"buy": None, "sell": None, "updated": None}
                    }
                },
                {
                    "id": 10,
                    "name": "Obmin Valyut",
                    "address": "вул. Михайла Драгоманова, 2, Київ",
                    "district": "Позняки/Харківський масив",
                    "phone": "",
                    "lat": 50.4089,
                    "lon": 30.6534,
                    "rates": {
                        "USD": {"buy": None, "sell": None, "updated": None},
                        "EUR": {"buy": None, "sell": None, "updated": None}
                    }
                }
            ]
            self._write_json(self.exchangers_file, initial_exchangers)
        
        # Инициализация rates_history.json
        if not os.path.exists(self.rates_history_file):
            self._write_json(self.rates_history_file, {})
        
        # Инициализация user_alerts.json
        if not os.path.exists(self.user_alerts_file):
            self._write_json(self.user_alerts_file, {})
        
        # Инициализация user_settings.json
        if not os.path.exists(self.user_settings_file):
            self._write_json(self.user_settings_file, {})
    
    def _read_json(self, filepath: str) -> Any:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка чтения {filepath}: {e}")
            return {} if 'history' in filepath or 'alerts' in filepath or 'settings' in filepath else []
    
    def _write_json(self, filepath: str, data: Any):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка записи {filepath}: {e}")
    
    # === EXCHANGERS ===
    def get_exchangers(self) -> List[Dict]:
        return self._read_json(self.exchangers_file)
    
    def get_exchanger_by_id(self, exchanger_id: int) -> Optional[Dict]:
        exchangers = self.get_exchangers()
        for ex in exchangers:
            if ex.get('id') == exchanger_id:
                return ex
        return None
    
    def add_exchanger(self, name: str, address: str, district: str, 
                     lat: float, lon: float, phone: str = "") -> Dict:
        exchangers = self.get_exchangers()
        new_id = max([ex.get('id', 0) for ex in exchangers], default=0) + 1
        
        new_exchanger = {
            "id": new_id,
            "name": name,
            "address": address,
            "district": district,
            "phone": phone,
            "lat": lat,
            "lon": lon,
            "rates": {
                "USD": {"buy": None, "sell": None, "updated": None},
                "EUR": {"buy": None, "sell": None, "updated": None}
            }
        }
        
        exchangers.append(new_exchanger)
        self._write_json(self.exchangers_file, exchangers)
        return new_exchanger
    
    def update_exchanger_rate(self, exchanger_id: int, currency: str, 
                             buy: float, sell: float):
        exchangers = self.get_exchangers()
        
        for ex in exchangers:
            if ex.get('id') == exchanger_id:
                ex['rates'][currency] = {
                    'buy': buy,
                    'sell': sell,
                    'updated': datetime.now().isoformat()
                }
                break
        
        self._write_json(self.exchangers_file, exchangers)
    
    # === RATES HISTORY ===
    def save_rate(self, source: str, currency: str, buy: float, sell: float):
        history = self._read_json(self.rates_history_file)
        
        if currency not in history:
            history[currency] = {}
        
        if source not in history[currency]:
            history[currency][source] = []
        
        history[currency][source].append({
            'buy': buy,
            'sell': sell,
            'timestamp': datetime.now().isoformat()
        })
        
        # Храним только последние 1000 записей для каждого источника
        if len(history[currency][source]) > 1000:
            history[currency][source] = history[currency][source][-1000:]
        
        self._write_json(self.rates_history_file, history)
    
    def get_rate_history(self, currency: str, source: str, 
                        hours: int = 24) -> List[Dict]:
        history = self._read_json(self.rates_history_file)
        
        if currency not in history or source not in history[currency]:
            return []
        
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        rates = history[currency][source]
        filtered = [
            r for r in rates 
            if datetime.fromisoformat(r['timestamp']) > cutoff_time
        ]
        
        return filtered
    
    # === USER SETTINGS ===
    def get_user_language(self, user_id: int) -> str:
        settings = self._read_json(self.user_settings_file)
        return settings.get(str(user_id), {}).get('language', 'uk')
    
    def set_user_language(self, user_id: int, language: str):
        settings = self._read_json(self.user_settings_file)
        
        if str(user_id) not in settings:
            settings[str(user_id)] = {}
        
        settings[str(user_id)]['language'] = language
        settings[str(user_id)]['updated'] = datetime.now().isoformat()
        
        self._write_json(self.user_settings_file, settings)
    
    def get_all_users(self) -> List[int]:
        settings = self._read_json(self.user_settings_file)
        return [int(uid) for uid in settings.keys()]
    
    # === USER ALERTS ===
    def get_user_alerts(self, user_id: int) -> List[Dict]:
        alerts = self._read_json(self.user_alerts_file)
        return alerts.get(str(user_id), [])
    
    def add_alert(self, user_id: int, currency: str, alert_type: str, 
                  threshold: float):
        alerts = self._read_json(self.user_alerts_file)
        
        if str(user_id) not in alerts:
            alerts[str(user_id)] = []
        
        new_alert = {
            'id': len(alerts[str(user_id)]) + 1,
            'currency': currency,
            'type': alert_type,  # 'percent' или 'price'
            'threshold': threshold,
            'active': True,
            'created': datetime.now().isoformat()
        }
        
        alerts[str(user_id)].append(new_alert)
        self._write_json(self.user_alerts_file, alerts)
        
        return new_alert
    
    def delete_alert(self, user_id: int, alert_id: int):
        alerts = self._read_json(self.user_alerts_file)
        
        if str(user_id) in alerts:
            alerts[str(user_id)] = [
                a for a in alerts[str(user_id)] 
                if a.get('id') != alert_id
            ]
            self._write_json(self.user_alerts_file, alerts)
    
    def get_all_alerts(self) -> Dict:
        return self._read_json(self.user_alerts_file)


# Глобальный экземпляр
storage = Storage()

