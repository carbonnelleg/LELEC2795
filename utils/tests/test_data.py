import os
import sys
try:
    import utils
except ModuleNotFoundError:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    utils_path = os.path.abspath(current_dir + '../../..')
    sys.path.append(utils_path)
    import utils
    del current_dir, utils_path
finally:
    from utils import Root, get_root, DataType, ns

elem = get_root('Data/# of Iterations (1264).data')

try:
    test_data = DataType(elem)
    print(test_data)
except AssertionError:
    print('test_data.tag got a wrong value and should be either p.DefaultValue, Array, Elem or Field')

try:
    item = elem.find('.//lv:DataItem', ns)
    test_data = DataType(item.find('lv:p.DefaultValue', ns))
    print(test_data)
except Exception:
    print('test failed')
