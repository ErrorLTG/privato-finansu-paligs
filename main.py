from kivy.app import App
import sqlite3
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from datetime import datetime
from kivy.uix.label import Label



class IncomeWindow(Screen):
    def callbackConfirm(self):
        Asistents.sendIncome(self)
        Asistents.getBudgetValue(self)

class ExpenseWindow(Screen):
    def callbackConfirm(self):
        Asistents.sendExpense(self)
        Asistents.getBudgetValue(self)
class WindowManager(ScreenManager):
    pass


kv = Builder.load_file("asistents.kv")


class Asistents(App): # Izveido programmas klasi
    def build(self):
        main = Asistents()
        main.getBudgetValue()
        main.addHistory("+")
        main.addHistory("-")
        return kv
    
    

    def addHistory(self, operation):
        if operation == "+":
            screen = "incomeScreen"
        else:
            screen = "expenseScreen"

        neededScreen = kv.get_screen(screen)
        layout = neededScreen.ids.historyLayout
        widgetText = ""
        posY = 0.775
        
        
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        query = f"SELECT shortDate, action FROM userData WHERE action LIKE '{operation}%' ORDER BY id DESC LIMIT 5"
        cursor.execute(query)
        results = cursor.fetchall()
        for result in results:
            widgetText = f"{result[0]} {result[1]}€"
            posY = posY - 0.05
            widget = Label(text=widgetText, font_size=15, pos_hint={"center_x": 0.5, "top": posY}, size_hint=(0.2, 0.3), padding = (0,0,0,5))
            layout.add_widget(widget)
        cursor.close()

    def deleteHistory(operation):
        if operation == "+":
            screen = "incomeScreen"
        else:
            screen = "expenseScreen"

        neededScreen = kv.get_screen(screen)
        layout = neededScreen.ids.historyLayout
        layout.clear_widgets()



    def getBudgetValue(self):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        query = "SELECT budget FROM userData ORDER BY id DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchall()
        kv.get_screen("incomeScreen").ids.budgetLabel.text = f"{result[0][0]}€"
        kv.get_screen("expenseScreen").ids.budgetLabel.text = f"{result[0][0]}€"
        
        cursor.close()

    def sendIncome(self):
        income = int(kv.get_screen("incomeScreen").ids.incomeValue.text)

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        cursor.execute("SELECT budget FROM userData ORDER BY id DESC LIMIT 1")
        oldBudget = cursor.fetchall()
        oldBudget= oldBudget[0][0]
        newBudget = oldBudget + income
        
        cursor.execute("SELECT MAX(id) FROM userData")
        previousId = cursor.fetchall()
        previousId = previousId[0][0]
        nextId = previousId + 1

        date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        shortDate = datetime.now().strftime("%d-%m %H:%M")

        action = f"+{income}"

        cursor.execute("INSERT INTO userData(id, date, shortDate, action, budget) VALUES (?,?,?,?,?)", (nextId, date, shortDate, action, newBudget))
        connection.commit()
        cursor.close()
        Asistents.deleteHistory("+")
        Asistents.addHistory(self, "+")

    def sendExpense(self):
        expense = int(kv.get_screen("expenseScreen").ids.expenseValue.text)

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        cursor.execute("SELECT budget FROM userData ORDER BY id DESC LIMIT 1")
        oldBudget = cursor.fetchall()
        oldBudget= oldBudget[0][0]
        newBudget = oldBudget - expense
        
        cursor.execute("SELECT MAX(id) FROM userData")
        previousId = cursor.fetchall()
        previousId = previousId[0][0]
        nextId = previousId + 1

        date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        shortDate = datetime.now().strftime("%d-%m %H:%M")

        action = f"-{expense}"

        cursor.execute("INSERT INTO userData(id, date, shortDate, action, budget) VALUES (?,?,?,?,?)", (nextId, date, shortDate, action, newBudget))
        connection.commit()
        cursor.close()
        Asistents.deleteHistory("-")
        Asistents.addHistory(self, "-")
if __name__ == "__main__":
    Asistents().run()