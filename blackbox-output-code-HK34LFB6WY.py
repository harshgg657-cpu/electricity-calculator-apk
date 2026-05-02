from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
import json
import os
from datetime import datetime, timedelta

FILE = "electricity_data.json"
RATE = 7.5

class ElectricityCalculatorApp(App):
    def build(self):
        self.rates = {
            'fan': 0.0625, 'ceiling': 0.0833, 'fridge': 0.05,
            'induction': 2.0, 'tv': 0.04, 'light': 0.07, 'charger': 0.033
        }
        self.data = self.load_data()
        self.entries = {}
        self.history_visible = False
        
        main = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        title = Label(text='Electricity Calculator', size_hint_y=None, height=dp(60),
                     font_size='24sp', bold=True, color=(0, 0.82, 1, 1))
        main.add_widget(title)
        
        input_frame = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(300),
                               padding=dp(15), spacing=dp(10))
        input_label = Label(text='Daily Usage Hours', size_hint_y=None, height=dp(40),
                           font_size='18sp', bold=True, color=(0, 0.82, 1, 1))
        input_frame.add_widget(input_label)
        
        self.input_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(220))
        appliances = [
            ('Fan', 'fan'), ('Ceiling Fan', 'ceiling'),
            ('Fridge', 'fridge'), ('Induction', 'induction'),
            ('TV', 'tv'), ('Lights', 'light')
        ]
        
        for name, key in appliances:
            lbl = Label(text=f'{name}:', size_hint_y=None, height=dp(35),
                       font_size='14sp', color=(0.88, 0.9, 0.93, 1))
            self.input_grid.add_widget(lbl)
            
            entry = TextInput(multiline=False, input_filter='float', font_size='16sp',
                             size_hint_y=None, height=dp(35), halign='center')
            entry.background_color = (0.1, 0.1, 0.18, 1)
            entry.foreground_color = (0, 0.82, 1, 1)
            self.input_grid.add_widget(entry)
            self.entries[key] = entry
        
        input_frame.add_widget(self.input_grid)
        main.add_widget(input_frame)
        
        btn_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        self.add_btn = Button(text='ADD TODAYS DATA', size_hint_y=None, height=dp(55),
                             background_color=(0, 0.82, 1, 1), color=(0,0,0,1),
                             font_size='16sp', bold=True)
        self.add_btn.bind(on_press=self.add_entry)
        btn_layout.add_widget(self.add_btn)
        
        self.history_btn = Button(text='Show History', size_hint_y=None, height=dp(55),
                                 background_color=(0.39, 0.45, 0.54, 1), color=(1,1,1,1),
                                 font_size='16sp', bold=True)
        self.history_btn.bind(on_press=self.toggle_history)
        btn_layout.add_widget(self.history_btn)
        main.add_widget(btn_layout)
        
        self.display_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        self.day_label = Label(text='Next Entry: Day 1', size_hint_y=None, height=dp(30),
                              font_size='16sp', color=(0.72, 0.74, 0.78, 1))
        self.display_layout.add_widget(self.day_label)
        
        self.today_value = self.create_card(self.display_layout, "TODAYS USAGE", (0.32, 0.81, 0.4, 1), 0.0)
        self.monthly_value = self.create_card(self.display_layout, "MONTHLY ESTIMATE", (1, 0.83, 0.23, 1), 0)
        self.bill_value = self.create_card(self.display_layout, "ESTIMATED BILL", (1, 0.42, 0.42, 1), 0)
        main.add_widget(self.display_layout)
        
        self.status_label = Label(text='Enter usage hours and click ADD', size_hint_y=None, height=dp(30),
                                 font_size='14sp', color=(0.72, 0.74, 0.78, 1))
        main.add_widget(self.status_label)
        
        self.history_frame = BoxLayout(orientation='vertical', size_hint_y=None, height=0)
        self.history_scroll = ScrollView(size_hint_y=None, height=0)
        self.history_list = Label(text='', size_hint_y=None, height=0, halign='left', valign='top',
                                 text_size=(None, None), font_size='14sp', color=(0.88