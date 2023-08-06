import unittest
from locust_nest.test import DATA_PATH

from locust_nest.nest import (
    load_dir,
    load_locust_dir,
    load_taskset_dir,
    load_config,
    collect_tasksets,
    collect_locusts
)

from locust.main import (
    load_locustfile,
    load_tasksetfile,
    is_taskset,
    is_locust
) # these functions are testing in ps-george/locust


class NestCase(unittest.TestCase):

    def test_load_dir(self):
        def checks(tasksets, locusts):
            # Test that tasksets are all tasksets and none are locusts.
            taskset_tuples = [(name,obj) for name, obj in tasksets.items()]
            for taskset in taskset_tuples:
                self.assertEqual(True, is_taskset(taskset))
                self.assertEqual(False, is_locust(taskset))

            # Test that all locusts are locusts
            locust_tuples = [(name,obj) for name, obj in locusts.items()]
            for locust in locust_tuples:
                self.assertEqual(True, is_locust(locust))
            self.assertEqual(False, is_taskset(locust))
            # Check that ExampleModel is found as a taskset
            # Check that ExampleModelLocust is found as a locust
            self.assertTrue('ExampleModel' in [name for name, _ in taskset_tuples])
            locust_names = [name for name, _ in locust_tuples]
            self.assertTrue('ExampleModelLocust' in locust_names)
            self.assertFalse('_PrivateExample' in locust_names)

        locusts = load_dir(DATA_PATH, load_locustfile)
        tasksets = load_dir(DATA_PATH, load_tasksetfile)
        checks(tasksets,locusts)        
        
        locusts2 = load_dir(DATA_PATH, load_locustfile, ignore_prefix='E')
        print(locusts2)
        locust_names2 = [name for name in locusts2.keys()]
        self.assertFalse('ExampleModelLocust' in locust_names2)
        self.assertTrue('_PrivateExample' in locust_names2)
    
        locusts_specific =  load_locust_dir(DATA_PATH)
        tasksets_specific =  load_taskset_dir(DATA_PATH)
        checks(tasksets_specific, locusts_specific)


    def test_load_config(self):
        config = load_config('{0}/config.json'.format(DATA_PATH))
        locusts = config.get('locusts')
        tasksets = config.get('tasksets')
        self.assertEqual(2, locusts.get('ExampleModelLocust'))
        self.assertEqual(1, tasksets.get('ExampleModel'))
        self.assertEqual(2, config.get('total_locusts'))
        self.assertEqual(1, config.get('total_tasksets'))
    

    def test_collect(self):
        # NOTE: format from collect_tasksets and collect_locusts is different
        tasks = collect_tasksets(DATA_PATH, '{0}/config.json'.format(DATA_PATH))
        locusts = collect_locusts(DATA_PATH, '{0}/config.json'.format(DATA_PATH))
        # print(tasks, locusts)
        # <class 'example.ExampleModelLoucst'>
        self.assertEqual([("<class 'example.ExampleModel'>", 1)], [(str(key),value) for key, value in tasks.items()])
        self.assertEqual([("<class 'example.ExampleModelLocust'>", 2)], [(str(cname),w) for cname,w in locusts])


if __name__=="__main__":
    unittest.main()