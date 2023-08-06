from functools import reduce, wraps
from itertools import chain, cycle, dropwhile, islice, takewhile, zip_longest
from typing import Any, Dict, Generic, Iterable, Sequence, Tuple, Union

from streamAPI.stream.decos import check_pipeline, close_pipeline
from streamAPI.stream.optional import EMPTY, Optional
from streamAPI.stream.streamHelper import (ChainedCondition, Closable, GroupByValueType, ListType,
                                           Supplier)
from streamAPI.utility.Types import (BiFunction, Callable, Consumer,
                                     Function, T, X, Y, Z)
from streamAPI.utility.utils import (Filter, divide_in_chunk,
                                     get_functions_clazz, identity)

NIL = object()


class Stream(Closable, Generic[X]):
    """
    This class can be used to create pipeline operation on given
    iterable object.
    There are two type of operation that can be performed on Stream:
    1) Intermediate (i.e. map, flat_map, filter, peek, distinct, sort, batch, cycle, take_while, drop_while etc.)
    2) Terminal (min, max, as_seq, group_by, partition, all, any, none_match, for_each)

    Until terminal operation is called, no execution takes place.
    Some of the examples are given below.
    
    Example:
        class Student:
            def __init__(self, name, age, sex):
                self.name = name
                self.age = age
                self.sex = sex

            def get_age(self):
                return self.age

            def __str__(self):
                return '[name='+self.name+',age='+str(self.age)+',sex='+('Male' if self.sex else 'Female')+']'

            def __repr__(self):
                return str(self)

        students = [Student('A',10,True),
                    Student('B',8,True),
                    Student('C',11,False),
                    Student('D',17,True),
                    Student('D',25,False),
                    Student('F',9,False),
                    Student('G',29,True)]

        Stream(students).filter(lambda x:x.age<20).sort(lambda x:x.age).as_seq()
        -> [[name=B,age=8,sex=Male],
            [name=F,age=9,sex=Female],
            [name=A,age=10,sex=Male],
            [name=C,age=11,sex=Female],
            [name=D,age=17,sex=Male]]

        Stream(students).filter(lambda x:x.age<20).partition(lambda x:x.sex)
        -> {True: [[name=A,age=10,sex=Male],
                   [name=B,age=8,sex=Male],
                   [name=D,age=17,sex=Male]],
            False: [[name=C,age=11,sex=Female],
                    [name=F,age=9,sex=Female]]}

        Stream(range(10)).map(lambda x: x**3 - x**2).filter(lambda x: x%3 == 0).distinct().limit(3).as_seq()
        ->  [0, 294, 648] # distinct can change the stream data ordering.

        Stream(range(10)).batch(3).as_seq() -> [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]

        Stream([(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]).flat_map().limit(6).as_seq()
        -> [0, 1, 2, 3, 4, 5]

        Stream(range(10)).take_while(lambda x:x<5).as_seq() # similar to while loop
        -> [0, 1, 2, 3, 4]

        Stream(range(10)).drop_while(lambda x:x<5).as_seq()
        -> [5, 6, 7, 8, 9]

        Stream(range(3,9)).zip(range(4)).as_seq() -> [(3, 0), (4, 1), (5, 2), (6, 3)]

        Stream(range(3,9)).zip(range(4),after=False).as_seq() -> [(0, 3), (1, 4), (2, 5), (3, 6)]

        Stream(range(3,9)).zip_longest(range(4),fillvalue=-1).as_seq()
        -> [(3, 0), (4, 1), (5, 2), (6, 3), (7, -1), (8, -1)]

        Stream(range(3,9)).zip_longest(range(4),after=False,fillvalue=-1).as_seq()
        -> [(0, 3), (1, 4), (2, 5), (3, 6), (-1, 7), (-1, 8)]

        Stream(range(10)).map(lambda x:x**2).reduce(lambda x,y:x+y) # sum of squares
        -> Optional[285]

    """

    def __init__(self, data: Iterable[X]):
        super().__init__()

        self._pointer = iter(data)
        self._closed = False

    @classmethod
    def from_supplier(cls, func: Callable[[], X], *args, **kwargs) -> 'Stream[X]':
        """
        Generates a stream from a callable function.

        :param func:
        :param args: positional arguments required instantiate cls
        :param kwargs: kwargs required for cls.
        :return:
        """

        return cls(Supplier(func), *args, **kwargs)

    @check_pipeline
    def map(self, func: Function[X, Y]) -> 'Stream[Y]':
        """
        maps elements of stream and produces stream of mapped element.

        Example:
            stream = Stream(range(5)).map(lambda x: 2*x)
            print(list(stream)) # prints [0, 2, 4, 6, 8]

        :param func:
        :return: Stream itself
        """

        self._pointer = map(func, self._pointer)
        return self

    @check_pipeline
    def filter(self, predicate: Filter[X]) -> 'Stream[X]':
        """
        Filters elements from Stream.

        Example:
            stream = Stream(range(5)).filter(lambda x: x%2 == 1)
            print(list(stream)) # prints [1, 3]

        :param predicate:
        :return: Stream itself
        """

        self._pointer = filter(predicate, self._pointer)
        return self

    @check_pipeline
    def sort(self, comp=None, reverse: bool = False) -> 'Stream[X]':
        """
        Sorts element of Stream.

        Example1:
            stream = Stream([3,1,4,6]).sort()
            list(stream) -> [1, 3, 4, 6]

            Stream([3,1,4,6]).sort(reverse=True).as_seq() -> [6, 4, 3, 1]

        Example2:
            class Student:
                def __init__(self, name, age):
                    self.name = name
                    self.age = age

                def get_age(self):
                    return self.age

                def __str__(self):
                    return '[name='+self.name+',age='+str(self.age)+']'

                def __repr__(self):
                    return str(self)

            students = [Student('A',3),Student('B',1),Student('C',4),Student('D',6)]

            Stream(students).sorted(comp=Student.get_age,reverse=True).as_seq()
            -> [[name=D,age=6], [name=C,age=4], [name=A,age=3], [name=B,age=1]]

        :param comp:
        :param reverse:
        :return: Stream itself
        """

        self._pointer = sorted(self._pointer, key=comp, reverse=reverse)
        return self

    @check_pipeline
    def distinct(self) -> 'Stream[X]':
        """
        uses distinct element of for further processing.

        Example:
            stream = Stream([4,1,6,1]).distinct()
            list(stream) -> [1, 4, 6]

        Note that, sorting is not guaranteed.
        Elements must be hashable and define equal logic(__eq__)

        :return:  Stream itself
        """

        self._pointer = Stream._yield_distinct(self._pointer)
        return self

    @staticmethod
    def _yield_distinct(itr: Iterable[X]):
        """
        yield distinct elements from a given iterable
        :param itr:
        :return:
        """
        consumer_items = set()

        for item in itr:
            if item not in consumer_items:
                yield item
                consumer_items.add(item)

    @check_pipeline
    def limit(self, n: int) -> 'Stream[X]':
        """
        limits number of element in stream.

        Example:
            stream = Stream(range(10)).limit(3)
            list(stream) -> [0,1,2]

        :param n:
        :return:
        """

        self._pointer = islice(self._pointer, n)
        return self

    @check_pipeline
    def peek(self, consumer: Consumer[X]) -> 'Stream[X]':
        """
        processes element while streaming.

        Example:
            def f(x): return 2*x

            stream = Stream(range(5)).peek(print).map(f)
            list(stream) first prints 0 to 4 and then makes a list of [0, 2, 4, 6, 8]

        :param consumer:
        :return: Stream itself
        """

        self._pointer = Stream._consumer_wrapper(consumer)(self._pointer)
        return self

    @check_pipeline
    def peek_after_each(self, consumer: Consumer[X], n: int) -> 'Stream[X]':
        """
        processes element while streaming. Consumer is called after each nth item.
        Example:
            def f(x): return 2*x

            stream = Stream(range(10)).peek_after_each(print,3).map(f)
            list(stream) first prints "2\n5\n8" and then makes a list
            [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

        :param consumer:
        :param n:
        :return: Stream itself
        """

        assert n > 0, 'n should be positive'

        self._pointer = Stream._consumer_wrapper(consumer, n=n)(self._pointer)
        return self

    @staticmethod
    def _consumer_wrapper(consumer: Consumer[X], n: int = 1):
        """
        Creates a wrapper around consumer.

        :param consumer:
        :param n
        :return:
        """

        @wraps(consumer)
        def func(generator: Iterable[X]) -> Iterable[X]:
            one_to_n = cycle(range(1, n + 1))  # cycling numbers from 1 up to n

            for idx, g in zip(one_to_n, generator):
                if idx == n:
                    consumer(g)

                yield g

        return func

    @check_pipeline
    def skip(self, n: int) -> 'Stream[X]':
        """
        Skips n number of element from Stream

        Example:
            stream = Stream(range(10)).skip(7)
            list(stream) -> [7, 8, 9]

        :param n:
        :return:  Stream itself
        """

        self._pointer = islice(self._pointer, n, None)
        return self

    @check_pipeline
    def flat_map(self) -> 'Stream[X]':
        """
        flats the stream if each element is iterable.

        Example:
            stream = Stream([[1,2],[3,4,5]]).flat_map()
            list(stream) -> [1, 2, 3, 4, 5]

        :return:Stream itself
        """

        self._pointer = chain.from_iterable(self._pointer)
        return self

    @check_pipeline
    def batch(self, n: int):
        """
        creates batches of size n from stream.

        Example:
            Stream(range(10)).batch(3).as_seq()
            -> [(0, 1, 2), (3, 4, 5), (6, 7, 8), (9,)]

        :param n: batch size
        :return:
        """

        self._pointer = divide_in_chunk(self._pointer, n)
        return self

    @check_pipeline
    def enumerate(self, start=0):
        """
        create stream of tuples where first entry is index and
        another is data itself.

        Example:
            Stream(range(4,10)).enumerate().as_seq()
            -> [(0, 4), (1, 5), (2, 6), (3, 7), (4, 8), (5, 9)]

            Stream(range(4,10)).enumerate(10).as_seq()
             [(10, 4), (11, 5), (12, 6), (13, 7), (14, 8), (15, 9)]

        :param start
        :return:
        """

        self._pointer = enumerate(self._pointer, start=start)
        return self

    @check_pipeline
    def take_while(self, predicate: Filter[X]) -> 'Stream[X]':
        """
        processes the element of stream till the predicate returns True.
        It is similar to "while" keyword of python.

        Stream(range(10)).till(lambda x:x < 5).as_seq() -> [0,1,2,3,4]

        :param predicate:
        :return:
        """

        self._pointer = takewhile(predicate, self._pointer)
        return self

    @check_pipeline
    def drop_while(self, predicate: Filter[X]) -> 'Stream[X]':
        """
        drops elements until predicate returns False

        stream.Stream(range(10)).drop_while(lambda x : x < 5).as_seq() -> [5, 6, 7, 8, 9]

        :param predicate:
        :return:
        """

        self._pointer = dropwhile(predicate, self._pointer)
        return self

    @check_pipeline
    def zip(self, *itr: Iterable[Y], after=True) -> 'Stream[Tuple]':
        """
        zips stream with another Iterable object.

        We can specify whether to zip iterable after the stream of before
        the stream by using "after".

        zip operation will produce a stream which will be exhausted if either
        itr has been exhausted or underlying stream is exhausted.

        Example:
            Stream(range(100, 100000)).zip(range(5)).as_seq()
            -> [(100, 0), (101, 1), (102, 2), (103, 3), (104, 4)]

            Stream(range(5)).zip(range(100, 100000)).as_seq()
            -> [(0, 100), (1, 101), (2, 102), (3, 103), (4, 104)]

            Stream(range(20, 30)).zip(range(5),after=False).as_seq()
            # data from range(5) will be used as first entry of tuple created by zipping
            # stream with iterable
            -> [(0, 20), (1, 21), (2, 22), (3, 23), (4, 24)]

        :param itr:
        :param after
        :return:
        """

        if after:
            self._pointer = zip(self._pointer, *itr)
        else:
            self._pointer = zip(*itr, self._pointer)

        return self

    @check_pipeline
    def zip_longest(self, *itr: Iterable[Y], after=True, fillvalue=None) -> 'Stream[Tuple]':
        """
        Unlike zip method which limits resultant stream depending on smaller iterable,
        zip_longest allow stream generator even though smaller iterable has been exhausted.
        default filling value will be used from "fillvalue".

        Example:
            Stream(range(11, 13)).zip_longest(range(5)).as_seq()
            -> [(11, 0), (12, 1), (None, 2), (None, 3), (None, 4)]

            Stream(range(11, 13)).zip_longest(range(5),after=False,fillvalue=-1).as_seq()
            -> [(0, 11), (1, 12), (2, -1), (3, -1), (4, -1)]

        :param itr:
        :param after:
        :param fillvalue:
        :return:
        """

        if after:
            self._pointer = zip_longest(self._pointer, *itr, fillvalue=fillvalue)
        else:
            self._pointer = zip_longest(*itr, self._pointer, fillvalue=fillvalue)

        return self

    @check_pipeline
    def cycle(self, itr: Iterable[Y], after=True) -> 'Stream[Tuple]':
        """
        Repeats iterable "itr" with stream until stream is exhausted.

        Example:
            Stream(range(11, 16)).cycle(range(3),after=False).as_seq()
            -> [(0, 11), (1, 12), (2, 13), (0, 14), (1, 15)]

        :param itr:
        :param after:
        :return:
        """

        return self.zip(cycle(itr), after=after)

    @check_pipeline
    def if_else(self, predicate: Filter[X],
                if_: Function[X, Y],
                else_: Function[X, Y] = identity) -> 'Stream[Y]':
        """
        if predicate returns True then elements are transformed according to if_ otherwise else_
        function is used. This method is the special case of "conditional" method. "else_" has
        default value "identity" which return element as it is; that is if "if" condition (predicate)
        does not return True then element is not modified.

        Example:
            Stream(range(10)).condition(lambda x: 3 <= x <= 7, lambda x: 1 , lambda x: 0).as_seq()
            -> [0, 0, 0, 1, 1, 1, 1, 1, 0, 0]

        :param predicate:
        :param if_:
        :param else_:
        :return:
        """

        return self.map(ChainedCondition.if_else(predicate, if_, else_).apply)

    @check_pipeline
    def conditional(self, chained_condition: ChainedCondition):
        """
        Transforming stream elements on the basis of given condition.

        Example:
            conditions = (ChainedCondition().if_then(lambda x : x < 3, lambda x : 0)
                          .if_then(lambda x: x < 7,lambda x: 1)
                          .otherwise(lambda x : 2))

            Stream(range(10)).conditional(condition).as_seq()
            ->  [0, 0, 0, 1, 1, 1, 1, 2, 2, 2]

            conditions = (ChainedCondition().if_then(lambda x : x < 3, lambda x : 0)
              .if_then(lambda x: x < 7,lambda x: 1).done())

            Stream(range(10)).conditional(condition).as_seq()
            -> [0, 0, 0, 1, 1, 1, 1, 7, 8, 9]


        :param chained_condition:
        :return:
        """

        return self.map(chained_condition.apply)

    def __next__(self) -> X:
        return next(self._pointer)

    @close_pipeline
    @check_pipeline
    def partition(self, mapper: Filter[X] = bool) -> Dict[bool, Sequence[X]]:
        """
        This operation is one of the terminal operations
        partition elements depending on mapper.

        Example:
            stream = Stream(range(6))
            stream.partition(mapper=lambda x: x%2) -> {0:[0, 2, 4], 1:[1, 3, 5]}

        :param mapper:
        :return: Stream itself
        """

        return self.group_by(mapper)

    @close_pipeline
    @check_pipeline
    def count(self) -> int:
        """
        This operation is one of the terminal operations

        Example:
            Stream(range(10)).count() -> 10

        :return: number of elements in Stream
        """

        return sum(1 for _ in self._pointer)

    @close_pipeline
    @check_pipeline
    def min(self, comp=None) -> Optional[Any]:
        """
        This operation is one of the terminal operations
        finds minimum element of Stream

        Example1:
            stream = Stream([3,1,5])
            item = stream.min().get() -> 1

        Example2:
            class Student:
                def __init__(self, name, age):
                    self.name = name
                    self.age = age

                def get_age(self):
                    return self.age

                def __str__(self):
                    return '[name='+self.name+',age='+str(self.age)+']'

                def __repr__(self):
                    return str(self)

            students = [Student('A',3),Student('B',1),Student('C',4),Student('D',6)]

            Stream(students).min(comp=Student.get_age) -> Optional[[name=B,age=1]]

        :param comp:
        :return:
        """

        try:
            return Optional(min(self._pointer, key=comp) if comp else min(self._pointer))
        except ValueError:
            return EMPTY

    @close_pipeline
    @check_pipeline
    def max(self, comp=None) -> Optional[Any]:
        """
        This operation is one of the terminal operations.
        finds maximum element of Stream

        Example1:
            stream = Stream([3,1,5])
            item = stream.max().get() -> 5

        Example2:
            class Student:
                def __init__(self, name, age):
                    self.name = name
                    self.age = age

                def get_age(self):
                    return self.age

                def __str__(self):
                    return '[name='+self.name+',age='+str(self.age)+']'

                def __repr__(self):
                    return str(self)

            students = [Student('A',3),Student('B',1),Student('C',4),Student('D',6)]

            Stream(students).max(comp=Student.get_age) -> Optional[[name=D,age=6]]

        :param comp:
        :return:
        """

        try:
            return Optional(max(self._pointer, key=comp) if comp else max(self._pointer))
        except ValueError:
            return EMPTY

    @close_pipeline
    @check_pipeline
    def group_by(self, key_hasher, value_mapper: Function[X, Y] = identity,
                 value_container_clazz: GroupByValueType = ListType) -> Dict[Any, Sequence[Y]]:
        """
        This operation is one of the terminal operations
        group by stream element using key_hasher.

        Example1:
            stream  = Stream(range(10))
            stream.group_by(key_hasher=lambda x: x%3) -> {0:[0, 3, 6, 9], 1:[1, 4, 7], 2:[2, 5, 8]}

        Example2:
            stream  = Stream(range(10))
            stream.group_by(key_hasher=lambda x: x%3,value_mapper=lambda x: x**2)
            -> {0:[0, 9, 36, 81], 1:[1, 16, 49], 2:[4, 25, 64]}

        Example3:
            out = Stream([1, 2, 3, 4, 2, 4]).group_by(lambda x:x%2,value_container_type=ListType)
            -> {1: [1, 3], 0: [2, 4, 2, 4]}

            out =Stream([1, 2, 3, 4, 2, 4]).group_by(lambda x:x%2,value_container_type=SetType)
            -> {1: {1, 3}, 0: {2, 4}}

        :param key_hasher:
        :param value_mapper:
        :param value_container_clazz:
        :return:
        """

        out = {}

        for elem in self._pointer:
            Stream._update(out, key_hasher(elem), value_mapper(elem), value_container_clazz)

        return out

    @staticmethod
    def _update(d: dict, k, v: X, value_container_clazz: GroupByValueType):
        if k not in d:
            pt = value_container_clazz()
            d[k] = pt
        else:
            pt = d[k]

        pt.add(v)

    @close_pipeline
    @check_pipeline
    def mapping(self, key_mapper: Function[X, T],
                value_mapper: Function[X, Y] = identity,
                resolve: BiFunction[Y, Y, Z] = None) -> Dict[T, Union[Y, Z]]:
        """
        This operation is one of the terminal operations
        creates mapping from stream element.

        Example:
            class Student:
                def __init__(self, name, id):
                    self.name = name
                    self.id  = id

            students = Stream([Student('a',1),Student('b',2),Student('a', 3)])
            students.mapping(key_mapper=lambda x:x.id, value_mapper=lambda x:x.name)
            -> {1: 'a', 2:'b', 3:'c'}
        Notice that elements after operated upon by function "key_mapper" must be
        unique. In case of duplicity, ValueError is thrown.

        for example:
            out = Stream([1,2,1,3]).mapping(lambda x:x, lambda x:x**2)

        will throw ValueError as a value (1) is present multiple times.

        In case we need to resolve such issues we can pass a function which
        will take oldValue and newValue and return a value which will be set
        for the key.

        out = Stream([1,2,3,4,5,6]).mapping(lambda x: x%2 ,lambda x:x, lambda o,n : o + n)
        print (out) # prints {0:12, 1: 9}


        :param key_mapper:
        :param value_mapper:
        :param resolve
        :return:
        """

        out = {}

        for elem in self._pointer:
            k = key_mapper(elem)

            if k in out:
                if resolve is None:
                    raise ValueError('key {} is already present in map'.format(k))
                out[k] = resolve(out[k], value_mapper(elem))
            else:
                out[k] = value_mapper(elem)

        return out

    @close_pipeline
    @check_pipeline
    def as_seq(self, seq_clazz: Callable[[Iterable[X], None], Y] = list, **kwargs) -> Y:
        """
        This operation is one of the terminal operations
        returns Stream elements as sequence, for example as list.

        Example:
            Stream(range(5)).as_seq() -> [1, 2, 3, 4, 5]

            from numpy import fromiter
            Stream(range(5)).as_seq(fromiter, dtype=int) -> array([0, 1, 2, 3, 4])

        :param seq_clazz:
        :param kwargs
        :return:
        """

        return seq_clazz(self._pointer, **kwargs)

    @close_pipeline
    @check_pipeline
    def all(self, predicate: Filter[X] = identity) -> bool:
        """
        This operation is one of the terminal operations
        returns True if all elements returns True. If there are no element in stream,
        returns True.

        Example:
            class Student:
                def __init__(self, name, age):
                    self.name = name
                    self.age  = age

            stream = Stream([Student('a',10), Student('b',12)])
            stream.all(predicate=lambda x:x.age < 15) -> True

            Stream([]).all() -> True # Empty Stream returns True
            Stream([0]).all() -> False
            Stream([1]).all() -> True

        :param predicate:
        :return:
        """

        return all(map(predicate, self._pointer))

    @close_pipeline
    @check_pipeline
    def any(self, predicate: Filter[X] = identity) -> bool:
        """
        This operation is one of the terminal operations
        Returns True if at-least one element are True according to given predicate.
        Consequently, empty Stream returns False.

        Example:
            class Student:
                def __init__(self, name, age):
                    self.name = name
                    self.age  = age

            stream = Stream([Student('a',10), Student('b',12)])
            stream.any(predicate=lambda x:x.age > 15) -> False

            Stream([]).any() -> False
            Stream([1]).any() -> True
            Stream([0]).any() -> False

        :param predicate:
        :return:
        """

        return any(map(predicate, self._pointer))

    @check_pipeline
    @close_pipeline
    def none_match(self, predicate: Filter[X] = identity) -> bool:
        """
        This operation is one of the terminal operations
        returns True if no element are true according to predicate.
        Empty stream returns True.
        Example:
            class Student:
                def __init__(self, name, age):
                    self.name = name
                    self.age  = age

            stream = Stream([Student('a',10), Student('b',12)])
            stream.none_match(predicate=lambda x:x.age > 11) -> False

        Example:
            stream = Stream([Student('a',10), Student('b',12)])
            stream.none_match(predicate=lambda x:x.age > 13) -> True

        Example:
            Stream([]).none_match(lambda x: x == 5) -> True
            Stream([1]).none_match(lambda x: x == 5) -> True
            Stream([1,5]).none_match(lambda x: x == 5) -> False

        :param predicate:
        :return:
        """

        return not self.any(predicate)

    @close_pipeline
    @check_pipeline
    def find_first(self) -> Optional[Any]:
        """
        This operation is one of the terminal operations
        finds first element from Stream.

        Example:
            Stream(range(4,9)).find_first() -> Optional[4]

        :return:
        """

        for g in self._pointer:
            return Optional(g)

        return EMPTY

    @close_pipeline
    @check_pipeline
    def for_each(self, consumer: Consumer[X]):
        """
        This operation is one of the terminal operations
        consumes each element from stream.
        Example:
            stream = Stream(range(5))
            stream.for_each(print)
            prints ->
            1
            2
            3
            4
            5

        :param consumer:
        """

        for g in self._pointer:
            consumer(g)

    @close_pipeline
    @check_pipeline
    def reduce(self, bi_func: BiFunction[X, X, Y], initial_point: X = NIL) -> Optional[Y]:
        """
        This operation is one of the terminal operations
        reduces stream element to produce an element.

        stream = Stream(range(1,6))
        stream.reduce(lambda x,y: x*y, 1) -> 120 (5!)

        Case Without initial point(initial__pointer is NIL):
            Return value can only be EMPTY iff Stream does not having
            any element left in it.

            SUMMING = lambda x,y : x + y

            Stream([]).reduce(SUMMING) -> EMPTY
            Stream([1]).reduce(SUMMING) -> Optional[1]
            Stream([1, 2]).reduce(SUMMING) -> Optional[3]

        Case With Initial Point (initial_point is not NIL):
            Return value will never be EMPTY.

            SUMMING = lambda x,y : x + y
            initial_point = 10

            Stream([]).reduce(SUMMING, initial_point) -> Optional[10]
            Stream([1]).reduce(SUMMING, initial_point) -> Optional[11]
            Stream([1, 2]).reduce(SUMMING, initial_point) -> Optional[13]

        :param initial_point:
        :param bi_func:
        :return:
        """

        if initial_point is not NIL:
            return Optional(reduce(bi_func, self._pointer, initial_point))
        else:
            try:
                return Optional(reduce(bi_func, self._pointer))
            except TypeError:
                return EMPTY

    @close_pipeline
    @check_pipeline
    def done(self):
        """
        This operation is one of the terminal operations.
        This can be used in case we are only interested in processing
        of elements.

        # TODO: add example
        :return:
        """

        for _ in self._pointer: pass

    @close_pipeline
    @check_pipeline
    def __iter__(self) -> Iterable[X]:
        """
        This operation is one of the terminal operations

        Example:
            for i in Stream(range(5)):
                print(i)

            prints: 1\n2\n3\n4\n5
        :return:iterator from stream
        """

        return iter(self._pointer)


if __name__ == 'streamAPI.stream.stream':
    __all__ = get_functions_clazz(__name__, __file__)
