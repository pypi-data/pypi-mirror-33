import unittest

class AmiciTest(unittest.TestCase):
    def test_import(self):
        import amici
    
    def test_wrap_sbml(self):
        """Create Python module from SBML model"""
        import amici
        sbmlImporter = amici.SbmlImporter('../examples/example_steadystate/model_steadystate_scaled.sbml')
        sbml = sbmlImporter.sbml
        
        observables = amici.assignmentRules2observables(sbml, filter=lambda variableId: 
                                                        variableId.startswith('observable_') and not variableId.endswith('_sigma'))
        
        print(observables)
        
        sbmlImporter.sbml2amici('test', 'test', 
                                observables=observables,
                                constantParameters=['k4'],
                                sigmas={'observable_x1withsigma': 'observable_x1withsigma_sigma'})

if __name__ == '__main__':
    unittest.main()
