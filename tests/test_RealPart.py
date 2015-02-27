#!/usr/bin/env python
import unittest
import ossie.utils.testing
import os
from time import sleep
from omniORB import any
from ossie.utils import sb

class ResourceTests(ossie.utils.testing.ScaComponentTestCase):
    """Test for all resource implementations in RealPart"""

    def setUp(self):
        #set up 
        ossie.utils.testing.ScaComponentTestCase.setUp(self)
        self.src = sb.DataSource()
        self.sink = sb.DataSink()
        
        #connect 
        self.startComponent()
        self.src.connect(self.comp)
        self.comp.connect(self.sink)
        
        #starts sandbox
        sb.start()

    def tearDown(self):
        #######################################################################
        # Simulate regular resource shutdown
        self.comp.releaseObject()
        
        self.comp.stop()
        sb.reset()
        sb.stop()
        ossie.utils.testing.ScaComponentTestCase.tearDown(self);


    def startComponent(self):
        #######################################################################
        # Launch the resource with the default execparams
        execparams = self.getPropertySet(kinds=("execparam",), modes=("readwrite", "writeonly"), includeNil=False)
        execparams = dict([(x.id, any.from_any(x.value)) for x in execparams])
        self.launch(execparams)

        #######################################################################
        # Verify the basic state of the resource
        self.assertNotEqual(self.comp, None)
        self.assertEqual(self.comp.ref._non_existent(), False)

        self.assertEqual(self.comp.ref._is_a("IDL:CF/Resource:1.0"), True)

        #######################################################################
        # Validate that query returns all expected parameters
        # Query of '[]' should return the following set of properties
        expectedProps = []
        expectedProps.extend(self.getPropertySet(kinds=("configure", "execparam"), modes=("readwrite", "readonly"), includeNil=True))
        expectedProps.extend(self.getPropertySet(kinds=("allocate",), action="external", includeNil=True))
        props = self.comp.query([])
        props = dict((x.id, any.from_any(x.value)) for x in props)
        # Query may return more than expected, but not less
        for expectedProp in expectedProps:
            self.assertEquals(props.has_key(expectedProp.id), True)

        #######################################################################
        # Verify that all expected ports are available
        for port in self.scd.get_componentfeatures().get_ports().get_uses():
            port_obj = self.comp.getPort(str(port.get_usesname()))
            self.assertNotEqual(port_obj, None)
            self.assertEqual(port_obj._non_existent(), False)
            self.assertEqual(port_obj._is_a("IDL:CF/Port:1.0"),  True)

        for port in self.scd.get_componentfeatures().get_ports().get_provides():
            port_obj = self.comp.getPort(str(port.get_providesname()))
            self.assertNotEqual(port_obj, None)
            self.assertEqual(port_obj._non_existent(), False)
            self.assertEqual(port_obj._is_a(port.get_repid()),  True)

        #######################################################################
        # Make sure start and stop can be called without throwing exceptions
        self.comp.start()


    # TODO Add additional tests here
    #
    # See:
    #   ossie.utils.bulkio.bulkio_helpers,
    #   ossie.utils.bluefile.bluefile_helpers
    # for modules that will assist with testing resource with BULKIO ports
    def testFunctionalityComplex(self):
        print "Testing Functionality for Complex Input"
        inputData = [complex(float(x+1), -float(x)) for x in xrange(100)]
        self.src.push(inputData)
        
        outData = []
        count = 0
        while True:
            outData = self.sink.getData()
            if outData:
                break
            if count == 100:
                break;
            sleep(.01)
            count+=1

        for x in xrange(len(outData)):
            self.assertEquals(outData[x], inputData[x].real)
            
    def testFunctionalityReal(self):
        print "Testing Functionality for Real Input"
        inputData = [float(x) for x in xrange(100)]
        self.src.push(inputData)
        
        outData = []
        count = 0
        while True:
            outData = self.sink.getData()
            if outData:
                break
            if count == 100:
                break;
            sleep(.01)
            count+=1

        for x in xrange(len(outData)):
            self.assertEquals(outData[x], inputData[x])
        

if __name__ == "__main__":
    ossie.utils.testing.main("../RealPart.spd.xml") # By default tests all implementations
