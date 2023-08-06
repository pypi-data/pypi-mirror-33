from interactive_search.console import InteractiveSearch
import os

result = InteractiveSearch(
    dataset=os.listdir('.')
).run()

print('Selected: %s' % result)
