from typing import Dict

class CodeHierarchySeq(list):
    def in_hierarchy(self) -> Dict:
        result = {}
        for habitat in self:
            codes = habitat.code.split('.')
            target = result
            while True:
                code = codes.pop(0)
                if not len(codes):
                    target[code] = habitat
                    break
                if code not in target:
                    target[code] = {}
                target = target[code]
        return result
