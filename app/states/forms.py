from aiogram.fsm.state import State,StatesGroup
class ProductForm(StatesGroup): code=State(); name=State(); price=State(); stock=State()
class TicketForm(StatesGroup): subject=State(); message=State()
