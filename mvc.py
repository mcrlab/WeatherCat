import tkinter as tk

class TodoModel:
   def __init__(self):
      self.tasks = []

   def add_task(self, task):
      self.tasks.append(task)

   def get_tasks(self):
      return self.tasks

class TodoView:
   def __init__(self, root, controller):
      self.root = root
      self.controller = controller

      self.task_entry = tk.Entry(root)
      self.task_entry.pack(pady=10)

      self.add_button = tk.Button(root, text="Add Task", command=self.controller.add_task)
      self.add_button.pack()

      self.task_listbox = tk.Listbox(root)
      self.task_listbox.pack()

   def update_task_list(self, tasks):
      self.task_listbox.delete(0, tk.END)
      for task in tasks:
         self.task_listbox.insert(tk.END, task)

class TodoController:
   def __init__(self, root):
      self.root = root
      self.model = TodoModel()
      self.view = TodoView(root, self)

   def add_task(self):
      task = self.view.task_entry.get()
      if task:
         self.model.add_task(task)
         self.view.update_task_list(self.model.get_tasks())
         self.view.task_entry.delete(0, tk.END)

def main():
   root = tk.Tk()
   root.title("Separating View and Controller")
   root.geometry("720x250")

   app = TodoController(root)
   root.mainloop()

if __name__ == "__main__":
   main()