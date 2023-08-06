
from promium.core.base import Element


class InputField(Element):

    @property
    def value(self):
        """Returns attribute value"""
        return self.get_attribute("value")

    @property
    def placeholder(self):
        """Returns attribute placeholder"""
        return self.get_attribute("placeholder")

    def clear(self):
        """Clears the text if it's a text entry element."""
        return self.lookup().clear()

    def set_value(self, value):
        """Sets data by the given value"""
        self.driver.execute_script(
            'arguments[0].value = "%s"' % value, self.lookup()
        )

    def send_keys(self, *value):
        """Sends keys by the given value"""
        return self.lookup().send_keys(*value)

    def clear_and_send_keys(self, value):
        """Execution 'clear' and 'send_keys'"""
        text = str(value)
        for _ in range(5):
            self.clear()
            self.send_keys(text)
            if self.value.lower() == text.lower():
                break
