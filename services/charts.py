import matplotlib
matplotlib.use('Agg')  # Важно! Для работы без GUI
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import List, Dict
import io


class ChartGenerator:
    def __init__(self):
        # Настройки стиля
        plt.style.use('seaborn-v0_8-darkgrid')
        self.colors = {
            'USD': '#2ecc71',
            'EUR': '#3498db',
            'line': '#e74c3c'
        }
    
    def generate_rate_chart(self, currency: str, data: List[Dict], 
                          period: str = 'day') -> io.BytesIO:
        """
        Генерация графика курса валюты
        
        Args:
            currency: Код валюты (USD, EUR)
            data: Список словарей с ключами timestamp, buy, sell
            period: Период (day, week, month)
        
        Returns:
            BytesIO объект с PNG изображением
        """
        if not data or len(data) < 2:
            return self._generate_no_data_chart(currency)
        
        # Извлекаем данные
        timestamps = [datetime.fromisoformat(d['timestamp']) for d in data]
        buy_rates = [d['buy'] for d in data]
        sell_rates = [d['sell'] for d in data]
        
        # Создаём фигуру
        fig, ax = plt.subplots(figsize=(12, 6), facecolor='#f8f9fa')
        ax.set_facecolor('#ffffff')
        
        # Рисуем линии
        ax.plot(timestamps, buy_rates, 
               label=f'Покупка', 
               color=self.colors.get(currency, '#2ecc71'),
               linewidth=2.5,
               marker='o',
               markersize=4)
        
        ax.plot(timestamps, sell_rates, 
               label=f'Продажа', 
               color=self.colors['line'],
               linewidth=2.5,
               marker='s',
               markersize=4,
               linestyle='--')
        
        # Заполнение между линиями
        ax.fill_between(timestamps, buy_rates, sell_rates, 
                       alpha=0.2, 
                       color=self.colors.get(currency, '#2ecc71'))
        
        # Настройка осей
        period_titles = {
            'day': 'День',
            'week': 'Тиждень',
            'month': 'Місяць'
        }
        
        ax.set_title(f'Динаміка курсу {currency}/UAH за {period_titles.get(period, "період")}', 
                    fontsize=16, 
                    fontweight='bold',
                    pad=20)
        
        ax.set_xlabel('Час', fontsize=12, fontweight='bold')
        ax.set_ylabel('Курс (₴)', fontsize=12, fontweight='bold')
        
        # Форматирование дат на оси X
        if period == 'day':
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        elif period == 'week':
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        else:  # month
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
        
        plt.xticks(rotation=45, ha='right')
        
        # Сетка
        ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
        
        # Легенда
        ax.legend(loc='upper left', 
                 frameon=True, 
                 shadow=True,
                 fontsize=11)
        
        # Добавляем текущее значение
        current_buy = buy_rates[-1]
        current_sell = sell_rates[-1]
        
        textstr = f'Поточний курс:\nПокупка: {current_buy:.2f} ₴\nПродаж: {current_sell:.2f} ₴'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax.text(0.02, 0.98, textstr, 
               transform=ax.transAxes,
               fontsize=10,
               verticalalignment='top',
               bbox=props)
        
        # Плотная компоновка
        plt.tight_layout()
        
        # Сохраняем в BytesIO
        buf = io.BytesIO()
        plt.savefig(buf, 
                   format='png', 
                   dpi=150, 
                   bbox_inches='tight',
                   facecolor='#f8f9fa')
        buf.seek(0)
        plt.close(fig)
        
        return buf
    
    def _generate_no_data_chart(self, currency: str) -> io.BytesIO:
        """Генерация заглушки когда нет данных"""
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#f8f9fa')
        ax.set_facecolor('#ffffff')
        
        ax.text(0.5, 0.5, 
               f'Недостатньо даних для\nпобудови графіка {currency}',
               ha='center', 
               va='center',
               fontsize=18,
               fontweight='bold',
               color='#95a5a6')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        buf = io.BytesIO()
        plt.savefig(buf, 
                   format='png', 
                   dpi=100,
                   bbox_inches='tight',
                   facecolor='#f8f9fa')
        buf.seek(0)
        plt.close(fig)
        
        return buf


# Глобальный экземпляр
chart_generator = ChartGenerator()

