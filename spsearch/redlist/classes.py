from typing import Iterable, List, Union
from itertools import dropwhile, zip_longest


class CodeHierarchySeq:
    def __init__(self, *args, codepoint: str ='', **kwargs):
        self._list = list(*args, **kwargs)
        self.codepoint = str(codepoint)

    def __iter__(self):
        return iter(self._list)

    def __getitem__(self, following_code: int):
        if isinstance(following_code, slice):
            raise SyntaxError('Use .slice() for slicing this object.')

        basecode = f'{self.codepoint}.{following_code}'.lstrip('.')

        def is_following_to_basecode(obj):
            basecode_split = basecode.split('.')
            target_code_split = obj.code.split('.')
            for i, _ in enumerate(basecode_split):
                try:
                    if basecode_split[i] != target_code_split[i]:
                        return False
                except IndexError:
                    return False
            return True

        returning = CodeHierarchySeq(filter(is_following_to_basecode, self), codepoint=basecode)
        if not returning:
            raise IndexError(f'Codepoint {basecode} does not match any.')
        return returning

    def slice(self, x):
        return self._list[x]

    def __str__(self):
        return str(self._list)

    def __repr__(self):
        return repr(self._list)

    def codes(self) -> List[int]:
        """Returns the code under this CodeHierarchy

        Example
        =======
        hierarchy = CodeHierarchySeq([
            <Threat 1.1: Housing & urban areas>,
            <Threat 1.2: Commercial & industrial areas>,
            <Threat 1.3: Tourism & recreation areas>,
            <Threat 2.4: Marine & freshwater aquaculture>,
            <Threat 2.4.3: Scale Unknown/Unrecorded>,
            <Threat 4.1: Roads & railroads>,
            <Threat 4.3: Shipping lanes>,
            <Threat 5.1: Hunting & trapping terrestrial animals>,
            <Threat 5.1.1: Intentional use (species is the target)>,
            <Threat 5.2: Gathering terrestrial plants>,
            <Threat 5.2.2: Unintentional effects (species is not the target)>,
            <Threat 5.4: Fishing & harvesting aquatic resources>,
            <Threat 5.4.4: Unintentional effects: (large scale) [harvest]>,
            <Threat 5.4.5: Persecution/control>,
            <Threat 6.1: Recreational activities>,
            <Threat 7.2: Dams & water management/use>,
            <Threat 7.2.11: Dams (size unknown)>,
            <Threat 7.2.4: Abstraction of surface water (unknown use)>,
            <Threat 9.1: Domestic & urban waste water>,
            <Threat 9.1.1: Sewage>,
            <Threat 9.1.3: Type Unknown/Unrecorded>,
            <Threat 9.2: Industrial & military effluents>,
            <Threat 9.2.1: Oil spills>,
            <Threat 9.2.3: Type Unknown/Unrecorded>,
            <Threat 9.3: Agricultural & forestry effluents>,
            <Threat 9.3.4: Type Unknown/Unrecorded>,
            <Threat 9.5: Air-borne pollutants>,
            <Threat 9.5.1: Acid rain>
        ])
        print(hierarchy.codes())    # [1, 2, 4, 5, 6, 7, 9]
        """
        codes = []
        for obj in self:
            codepoint_iter = iter(self.codepoint.split('.'))
            deeper_code = dropwhile(lambda x: x == next(codepoint_iter), obj.code)
            codes.append(int(next(deeper_code)))
        return sorted(list(set(codes)))


