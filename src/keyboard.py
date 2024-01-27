from .worker import Worker


default_params = {

}

class Keyboard(Worker):

  def __init__(self,
               stop_event=None, 
               params=None, 
               consumption_queue=None,
               publish_queue=None
               ):
    super().__init__(default_params, stop_event, params, consumption_queue)
    self.publish_queue = publish_queue

  def run(self):
    while not self.stop_event.is_set():
      print("Keyboard worker running")
      keybaord_input = input()
      self.publish_queue.put([keybaord_input])
    self.publish_queue.put(None)

