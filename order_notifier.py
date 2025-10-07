class OrderNotifier:
    listeners = []

    def register(self, model):
        self.listeners.append(model)

    def notify_new_id(self, old_id: int, new_id: int):
        for listener in self.listeners:
            listener.changed_id(old_id, new_id)
