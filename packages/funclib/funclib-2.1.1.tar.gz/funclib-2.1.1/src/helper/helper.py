from ..config.config import *

class Helper(object):
    _info = """
    ===================================================================================
                                        Func-Lib
                        A data processing methods lib for Python(2/3)
    -----------------------------------------------------------------------------------
                                Author: @CN-Tower
                            Create At: 2018-2-2
                            Update At: 2018-3-15
                                Version: """ + version + """
                                GitHub: http://github.com/CN-Tower/FuncLib
    -----------------------------------------------------------------------------------
        0: fn.info          1: fn.index         2: fn.find           3: fn.filter
        4: fn.reject        5: fn.reduce        6: fn.contains       7: fn.flatten
        8: fn.each          9: fn.uniq          10: fn.pluck         11: fn.pick
        12: fn.every        13: fn.some         14: fn.list          15: fn.drop
        16: fn.dump         17: fn.clone        18: fn.test          19: fn.replace
        20: fn.iscan        21: fn.log          22: fn.timer         23: fn.now
    ===================================================================================
    """
    _index = """ 
    ### fn.index
        Looks through the list and returns the item index. If no match is found,
        or if list is empty, -1 will be returned.
        eg:
            from funclib import fn
            persons = [{"name": "Tom", "age": 12},
                {"name": "Jerry", "age": 20},
                {"name": "Mary", "age": 35}]

            Jerry_idx = fn.index({"name": 'Jerry'}, persons)
            Mary_idx  = fn.index(lambda x: x['name'] == 'Mary', persons)

            print(Jerry_idx)  # => 1
            print(Mary_idx)   # => 2
    """
    _find = """
    ### fn.find
        Looks through each value in the list, returning the first one that passes
        a truth test (predicate), or None.If no value passes the test the function
        returns as soon as it finds an acceptable element, and doesn't traverse
        the entire list.
        eg:
            from funclib import fn
            persons = [{"name": "Tom", "age": 12},
                {"name": "Jerry", "age": 20},
                {"name": "Mary", "age": 35}]

            Jerry = fn.find({"name": 'Jerry'}, persons)
            Mary  = fn.find(lambda x: x['name'] == 'Mary', persons)

            print(Jerry)  # => {'age': 20, 'name': 'Jerry'}
            print(Mary)   # => {'age': 35, 'name': 'Mary'}
    """
    _filter = """
    ### fn.filter
        Looks through each value in the list, returning an array of all the values
        that pass a truth test (predicate).
        eg:
            from funclib import fn
            persons = [{"name": "Tom", "age": 20},
                        {"name": "Jerry", "age": 20},
                        {"name": "Jerry", "age": 35}]

            Jerry = fn.filter({"age": 20}, persons)
            Mary = fn.filter(lambda x: x['name'] == 'Jerry', persons)
            print(Jerry)  # => [{'age': 20, 'name': 'Tom'},
                                {'age': 20, 'name': 'Jerry'}]
            print(Mary)   # => [{'age': 20, 'name': 'Jerry'},
                                {'age': 35, 'name': 'Jerry'}]
    """
    _reject = """
    ### fn.reject
        Returns the values in list without the elements that the truth test (predicate)
        passes.
        The opposite of filter.
        eg:
            from funclib import fn
            persons = [{"name": "Tom", "age": 12},
                        {"name": "Jerry", "age": 20},
                        {"name": "Mary", "age": 35}]

            not_Mary = fn.reject({"name": "Mary"}, persons)
            adults = fn.reject(lambda x: x['age'] < 18, persons)

            print(not_Mary)  # => [{"age": 12, "name": "Tom"},
                                    {"age": 20, "name": "Jerry"}]
            print(adults)    # => [{"age": 20, "name": "Jerry"},
                                    {"age": 35, "name": "Mary"}]
    """
    _reduce = """
    ### fn.reduce
        Returns the buildIn method 'reduce', in python 3 the 'reduce' is imported
        from functools.
        eg:
            from funclib import fn
            num_list = [1 , 2, 3, 4]
            print(fn.reduce(lambda a, b: a + b, num_list))  # => 10
    """
    _contains = """
    ### fn.contains
        Returns true if the value is present in the list.
        eg:
            from funclib import fn
            persons = [{"name": "Tom", "age": 12},
                        {"name": "Jerry", "age": 20},
                        {"name": "Mary", "age": 35}]

            is_contains_Jerry = fn.contains({"name": "Jerry", "age": 12}, persons)
            is_contains_Mary = fn.contains(lambda x: x['name'] == 'Mary', persons)

            print(is_contains_Jerry)  # => False
            print(is_contains_Mary)   # => True
    """
    _flatten = """
    ### fn.flatten
        Flattens a nested array (the nesting can be to any depth). If you pass shallow,
        the array will only be flattened a single level.
        eg:
            from funclib import fn
            flt_list_01 = fn.flatten([1, [2], [3, [[4]]]])
            flt_list_02 = fn.flatten([1, [2], [3, [[4]]]], True)
            print(flt_list_01)  # => [1, 2, 3, [[4]]]
            print(flt_list_02)  # => [1, 2, 3, 4];
    """
    _each = """
    ### fn.each
        Produces a new values list by mapping each value in list through a transformation
        function (iteratee). 
        eg:
            from funclib import fn
            num_list = [1 , 2, 3, 4]
            list_10 = fn.each(lambda x: x % 2, num_list)
            print(list_10)  #=> [1, 0, 1, 0]
    """
    _uniq = """
    ### fn.uniq
        Produces a duplicate-free version of the array.
        In particular only the first occurence of each value is kept.
        eg:
            from funclib import fn
            persons00 = ("Tom", "Tom", "Jerry")
            persons01 = ["Tom", "Tom", "Jerry"]
            demo_list = [False, [], False, True, [], {}, False, '']
            persons02 = [{"name": "Tom", "age": 12, "pet": {"species": "dog", "name": "Kitty"}},
                            {"name": "Tom", "age": 20, "pet": {"species": "cat", "name": "wang"}},
                            {"name": "Mary", "age": 35, "pet": {"species": "cat", "name": "mimi"}}]

            unique_persons00 = fn.uniq(persons00)
            unique_persons01 = fn.uniq(persons01)
            unique_demo_list = fn.uniq(demo_list)
            unique_name = fn.uniq(persons02, 'name')
            unique_pet = fn.uniq(persons02, 'pet', 'species')

            print(unique_persons00)  # => ["Jerry", "Tom"]
            print(unique_persons01)  # => ["Jerry", "Tom"]
            print(unique_demo_list)  # => [False, [], True, {}, '']
    """
    _pluck = """
    ### fn.pluck
        Pluck the collections element.
        eg:
            from funclib import fn
            persons = [{"name": "Tom", "hobbies": ["sing", "running"]},
                {"name": "Jerry", "hobbies": []},
                {"name": "Mary", "hobbies": ['hiking', 'sing']}]

            hobbies = fn.pluck(persons, 'hobbies')
            hobbies_uniq = fn.pluck(persons, 'hobbies', uniq=True)

            print(hobbies)      # => ["sing", "running", 'hiking', 'sing']
            print(hobbies_uniq) # => ["sing", "running", 'hiking']
    """
    _pick = """
    ### fn.pick
        Pick values form dict or list.
        eg:
            from funclib import fn
            Tom = {
                "name": "Tom",
                "age": 12,
                "pets": [
                    {"species": "dog", "name": "Kitty"},
                    {"species": "cat", "name": "mimi"}
                ]
            }
            pets = fn.pick(Tom, 'age')
            first_pet_species = fn.pick(Tom, 'pets', [0], 'species')
            find_mimi_species = fn.pick(Tom, 'pets', {'name': 'mimi'}, 'species')
            find_dog_name = fn.pick(Tom, 'pets', lambda x: x['species'] == 'dog', 'name')
            print(pets)               # => 12
            print(first_pet_species)  # => dog
            print(find_mimi_species)  # => cat
            print(find_dog_name)      # => Kitty
    """
    _every = """
    ### fn.every
        Returns true if all of the values in the list pass the predicate truth test.
        Short-circuits and stops traversing the list if a false element is found.
        eg:
            from funclib import fn
            num_list = [1, 1, 2, 3, 5, 8]
            persons = [{"name": "Tom", "age": 12, "sex": "m"},
                        {"name": "Jerry", "age": 20, "sex": "m"},
                        {"name": "Mary", "age": 35, "sex": "f"}]

            is_all_five = fn.every(5, num_list)
            is_all_male = fn.every({"sex": "m"}, persons)
            is_all_adult = fn.every(lambda x: x['age'] > 18, persons)
            print(is_all_five)   # => False
            print(is_all_male)   # => False
            print(is_all_adult)  # => False
    """
    _some = """
    ### fn.some
        Returns true if any of the values in the list pass the predicate
        truth test. Short-circuits and stops traversing the list if a true
        element is found.
        eg:
            from funclib import fn
            num_list = [1, 1, 2, 3, 5, 8]
            persons = [{"name": "Tom", "age": 12, "sex": "m"},
                        {"name": "Jerry", "age": 20, "sex": "m"},
                        {"name": "Mary", "age": 35, "sex": "f"}]

            is_any_five = fn.some(5, num_list)
            is_any_male = fn.some({"sex": "m"}, persons)
            is_any_adult = fn.some(lambda x: x['age'] > 18, persons)
            print(is_any_five)   # => True
            print(is_any_male)   # => True
            print(is_any_adult)  # => True
    """
    _list = """
    ### fn.list
        Return now system time.
        eg:
            from funclib import fn
            print(fn.list())       # => []
            print(fn.list([]))     # => []
            print(fn.list({}))     # => [{}]
            print(fn.list(None))   # => [None]
            print(fn.list('test')) # => ['test']
    """
    _drop = """
    ### fn.drop
        Delete false values expect 0.
        eg:
            from funclib import fn
            tmp_list = [0, '', 3, None, [], {}, ['Yes'], 'Test']
            drop_val = fn.drop(tmp_list)
            without_0 = fn.drop(tmp_list, True)

            print(drop_val)  # => [3, ['Yes'], 'Test']
            print(without_0)  # => [0, 3, ['Yes'], 'Test']
    """
    _dump = """
    ### fn.dump
        Return a formatted json string.
        eg:
            from funclib import fn
            persons = [{"name": "Tom", "hobbies": ["sing", "running"]},
                {"name": "Jerry", "hobbies": []}]
            print(fn.dump(persons)) #=>
            [
                {
                "hobbies": [
                    "sing", 
                    "running"
                ], 
                "name": "Tom"
                }, 
                {
                "hobbies": [], 
                "name": "Jerry"
                }
            ]
    """
    _clone = """
    ### fn.clone
        Create a deep-copied clone of the provided plain object.
        eg:
            from funclib import fn
            persons = [{"name": "Tom", "age": 12},
                        {"name": "Jerry", "age": 20}]
            persons_01 = persons
            persons_02 = fn.clone(persons)
            fn.find({'name': 'Tom'}, persons)['age'] = 18

            print(persons_01)  # => [{"name": "Tom", "age": 18},
                                        {"name": "Jerry", "age": 20}]
            print(persons_02)  # => [{"name": "Tom", "age": 12},
                                        {"name": "Jerry", "age": 20}]
    """
    _test = """
    ### fn.test
        Check is the match successful, a boolean value will be returned.
        eg:
            from funclib import fn
            not_in = fn.test(r'ab', 'Hello World!')
            in_str = fn.test(r'll', 'Hello World!')
            print(not_in)  # => False
            print(in_str)  # => True
    """
    _replace = """
    ### fn.replace
        Replace sub string of the origin string with re.sub()
        eg:
            from funclib import fn
            greetings = 'Hello I\'m Tom!'
            print(fn.replace(r'Tom', 'Jack', greetings)) # => Hello I'm Jack!
    """
    _iscan = """
    ### fn.iscan
        Test is the expression valid, a boolean value will be returned.
        eg:
            from funclib import fn
            print(fn.iscan("int('a')"))  # => False
            print(fn.iscan("int('5')"))  # => True
    """
    _log = """
    ### fn.log
        Show log clear in console.
        eg:
            from funclib import fn
            persons = [{"name": "Tom", "hobbies": ["sing", "running"]},
                        {"name": "Jerry", "hobbies": []}]
            fn.log(persons)  # =>
===========================================================================
                        """ + log_title + """
---------------------------------------------------------------------------
[
  {
    "hobbies": [
      "sing", 
      "running"
    ], 
    "name": "Tom"
  }, 
  {
    "hobbies": [], 
    "name": "Jerry"
  }
]
===========================================================================
    """
    _timer = """
    ### fn.timer
        Set a timer with interval and timeout limit.
        eg: 
            from funclib import fn
            count = 0
            def fn():
                global count
                if count == 4:
                    return True
                count += 1
                print(count)

            fn.timer(fn, 10, 2)
            # =>
                >>> 1  #at 0s
                >>> 2  #at 2s
                >>> 3  #at 4s
                >>> 4  #at 4s
    """
    _now = """
    ### fn.now
        Return now system time.
        eg:
            from funclib import fn
            print(fn.now()) # => '2018-2-1 19:32:10'
    """
    
