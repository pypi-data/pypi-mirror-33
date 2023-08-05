"""
Constraint contains parent classes for all constraints.
A Constraint is used to set certain rules for the stochastic engine to
evolve the atomic system. Therefore it has become possible to fully
customize and set any possibly imaginable rule.

.. inheritance-diagram:: fullrmc.Core.Constraint
    :parts: 1
"""

# standard libraries imports
import os
import inspect
from random import random as randfloat

# external libraries imports
import numpy as np

# fullrmc imports
from fullrmc.Globals import INT_TYPE, FLOAT_TYPE, LOGGER
from fullrmc.Core.Collection import ListenerBase, is_number, is_integer, get_path
from fullrmc.Core.Collection import _AtomsCollector, reset_if_collected_out_of_date


class Constraint(ListenerBase):
    """ A constraint is used to direct the evolution of the atomic
    configuration towards the desired and most meaningful one.
    """
    def __init__(self):
        # init ListenerBase
        super(Constraint, self).__init__()
        # set engine
        self.__engine = None
        # set used flag
        self.set_used(True)
        # initialize variance squared
        self.__varianceSquared = 1
        # initialize atoms collector with datakeys to None. so it must be set in all subclasses.
        self._atomsCollector = _AtomsCollector(self, dataKeys=None)
        # initialize data
        self.__initialize_constraint()
        # computation cost
        #self.__computationCost = 0
        self.set_computation_cost(0)
        # set frame data
        FRAME_DATA  = ('_Constraint__state', '_Constraint__used',
                       '_Constraint__tried', '_Constraint__accepted',
                       '_Constraint__varianceSquared','_Constraint__standardError',
                       '_Constraint__originalData', '_Constraint__data',
                       '_Constraint__activeAtomsDataBeforeMove', '_Constraint__activeAtomsDataAfterMove',
                       '_Constraint__amputationData', '_Constraint__afterMoveStandardError',
                       '_Constraint__amputationStandardError', '_Constraint__computationCost',
                       '_atomsCollector')
        RUNTIME_DATA = ('_Constraint__state','_Constraint__tried', '_Constraint__accepted',
                        '_Constraint__varianceSquared','_Constraint__standardError','_Constraint__data',
                        '_atomsCollector',)
        object.__setattr__(self, 'FRAME_DATA',  FRAME_DATA   )
        object.__setattr__(self, 'RUNTIME_DATA',RUNTIME_DATA )


    def __setattr__(self, name, value):
        if name in ('FRAME_DATA','RUNTIME_DATA',):
            raise LOGGER.error("Setting '%s' is not allowed."%name)
        else:
            object.__setattr__(self, name, value)

    def __getstate__(self):
        state = {}
        for k, v in self.__dict__.items():
            if k in self.FRAME_DATA:
                continue
            else:
                state[k] = v
        return state

    def _set_engine(self, engine):
        assert self.__engine is None, LOGGER.error("Re-setting constraint engine is not allowed.")
        from fullrmc.Engine import Engine
        assert isinstance(engine, Engine),LOGGER.error("engine must be a fullrmc Engine instance")
        self.__engine = engine
        # set constraint unique id
        names = [c.constraintId for c in engine.constraints]
        idx = 0
        while True:
            name = self.__class__.__name__ + "_%i"%idx
            if name not in names:
                self.__constraintId = name
                break
            else:
                idx += 1
        # reset flags
        # resetting is commented because changing engine is not allowed anymore
        # and there is no need to reset_constraint anymore since at this poing all flag
        # are still and their reset value.
        #self.reset_constraint(reinitialize=False, flags=True, data=False)

    def __initialize_constraint(self):
        # initialize flags
        self.__state     = None
        self.__tried     = 0
        self.__accepted  = 0
        # initialize data
        self.__originalData              = None
        self.__data                      = None
        self.__activeAtomsDataBeforeMove = None
        self.__activeAtomsDataAfterMove  = None
        self.__amputationData            = None
        # initialize standard error
        self.__standardError           = None
        self.__afterMoveStandardError  = None
        self.__amputationStandardError = None
        # reset atoms collector # ADDED 2017-JAN-08
        self._atomsCollector.reset()
        self._on_collector_reset()
        if self.engine is not None and len(self._atomsCollector.dataKeys):
            for realIndex in self.engine._atomsCollector.indexes:
                self._on_collector_collect_atom(realIndex=realIndex)
        # dunp to repository
        self._dump_to_repository({'_Constraint__state'                    : self.__state,
                                  '_Constraint__tried'                    : self.__tried,
                                  '_Constraint__accepted'                 : self.__accepted,
                                  '_Constraint__varianceSquared'          : self.__varianceSquared,
                                  '_Constraint__originalData'             : self.__originalData,
                                  '_Constraint__data'                     : self.__data,
                                  '_Constraint__activeAtomsDataBeforeMove': self.__activeAtomsDataBeforeMove,
                                  '_Constraint__activeAtomsDataAfterMove' : self.__activeAtomsDataAfterMove,
                                  '_Constraint__amputationData'           : self.__amputationData,
                                  '_Constraint__standardError'            : self.__standardError,
                                  '_Constraint__afterMoveStandardError'   : self.__afterMoveStandardError,
                                  '_Constraint__amputationStandardError'  : self.__amputationStandardError,
                                  '_atomsCollector'                       : self._atomsCollector})

    @property
    def constraintId(self):
        """ Constraints unique id."""
        return self.__constraintId

    @property
    def engine(self):
        """ Stochastic fullrmc's engine instance."""
        return self.__engine

    @property
    def computationCost(self):
        """ Computation cost number."""
        return self.__computationCost

    @property
    def state(self):
        """ Constraint's state."""
        return self.__state

    @property
    def tried(self):
        """ Constraint's number of tried moves."""
        return self.__tried

    @property
    def accepted(self):
        """ Constraint's number of accepted moves."""
        return self.__accepted

    @property
    def used(self):
        """ Constraint's used flag. Defines whether constraint is used
        in the stochastic engine at runtime or set inactive."""
        return self.__used

    @property
    def varianceSquared(self):
        """ Constraint's varianceSquared used in the stochastic engine
        at runtime to calculate the total constraint's standard error."""
        return self.__varianceSquared

    @property
    def standardError(self):
        """ Constraint's standard error value."""
        return self.__standardError

    @property
    def originalData(self):
        """ Constraint's original data calculated upon initialization."""
        return self.__originalData

    @property
    def data(self):
        """ Constraint's current calculated data."""
        return self.__data

    @property
    def activeAtomsDataBeforeMove(self):
        """ Constraint's current calculated data before last move."""
        return self.__activeAtomsDataBeforeMove

    @property
    def activeAtomsDataAfterMove(self):
        """ Constraint's current calculated data after last move."""
        return self.__activeAtomsDataAfterMove

    @property
    def afterMoveStandardError(self):
        """ Constraint's current calculated StandardError after last move."""
        return self.__afterMoveStandardError

    @property
    def amputationData(self):
        """ Constraint's current calculated data after amputation."""
        return self.__amputationData

    @property
    def amputationStandardError(self):
        """ Constraint's current calculated StandardError after amputation."""
        return self.__amputationStandardError

    def _get_repository(self):
        if self.engine is None:
            return None
        else:
            return self.engine._get_repository()

    def _dump_to_repository(self, dataDict):
        rep = self._get_repository()
        if rep is None:
            return
        cp = os.path.join(self.engine.usedFrame, 'constraints', self.__constraintId)
        #print 'Constraint._dump_to_repository --> ', cp
        for name, value in dataDict.items():
            rep.dump(value=value, relativePath=cp, name=name, replace=True)

    def _set_original_data(self, data):
        """ Used only by the stochastic engine to set constraint's data as
        initialized for the first time."""
        self.__originalData = data
        # dump to repository
        self._dump_to_repository({'_Constraint__originalData' :self.__originalData})

    def _runtime_initialize(self):
        """
        This is called once everytime engine.run method is executed.
        It is meant to be used as a final setup call for all constraints.
        """
        pass

    def _runtime_on_step(self):
        """
        This is called at everytime engine.run method main loop step.
        """
        pass

    def set_variance_squared(self, value):
        """
        Set constraint's variance squared that is used in the c
        omputation of the total stochastic engine standard error.

        :Parameters:
            #. value (number): Any positive non zero number.
        """
        assert is_number(value), LOGGER.error("Variance squared accepted value must be convertible to a number")
        value = float(value)
        assert value>0 , LOGGER.error("Variance squared must be positive non zero number.")
        self.__varianceSquared = value

    def set_computation_cost(self, value):
        """
        Set constraint's computation cost value. This is used at stochastic
        engine runtime to minimize computations and enhance performance by
        computing less costly constraints first. At every step, constraints
        will be computed in order starting from the less to the most
        computationally costly. Therefore upon rejection of a step because
        of an unsatisfactory rigid constraint, the left un-computed
        constraints at this step are guaranteed to be the most time coslty
        ones.

        :Parameters:
            #. value (number): computation cost.
        """
        assert is_number(value), LOGGER.error("computation cost value must be convertible to a number")
        self.__computationCost  = FLOAT_TYPE(value)
        # dump to repository
        self._dump_to_repository({'_Constraint__computationCost' :self.__computationCost})

    @reset_if_collected_out_of_date # ADDED 2017-JAN-12
    def set_used(self, value):
        """
        Set used flag.

        :Parameters:
            #. value (boolean): True to use this constraint in stochastic
               engine runtime.
        """
        assert isinstance(value, bool), LOGGER.error("value must be boolean")
        self.__used = value
        # dump to repository
        self._dump_to_repository({'_Constraint__used' :self.__used})

    def set_state(self, value):
        """
        Set constraint's state. When constraint's state and stochastic
        engine's state don't match, constraint's data must be re-calculated.

        :Parameters:
            #. value (object): Constraint state value.
        """
        self.__state = value

    def set_tried(self, value):
        """
        Set constraint's number of tried moves.

        :Parameters:
            #. value (integer): Constraint tried moves value.
        """
        try:
            value = float(value)
        except:
            raise Exception(LOGGER.error("tried value must be convertible to a number"))
        assert is_integer(value), LOGGER.error("tried value must be integer")
        assert value>=0, LOGGER.error("tried value must be positive")
        self.__tried = int(value)

    def increment_tried(self):
        """ Increment number of tried moves. """
        self.__tried += 1

    def set_accepted(self, value):
        """
        Set constraint's number of accepted moves.

        :Parameters:
            #. value (integer): Constraint's number of accepted moves.
        """
        try:
            value = float(value)
        except:
            raise Exception(LOGGER.error("accepted value must be convertible to a number"))
        assert is_integer(value), LOGGER.error("accepted value must be integer")
        assert value>=0, LOGGER.error("accepted value must be positive")
        assert value<=self.__tried, LOGGER.error("accepted value can't be bigger than number of tried moves")
        self.__accepted = int(value)

    def increment_accepted(self):
        """ Increment constraint's number of accepted moves. """
        self.__accepted += 1

    def set_standard_error(self, value):
        """
        Set constraint's standardError value.

        :Parameters:
            #. value (number): standard error value.
        """
        self.__standardError = value

    def set_data(self, value):
        """
        Set constraint's data value.

        :Parameters:
            #. value (number): constraint's data.
        """
        self.__data = value

    def set_active_atoms_data_before_move(self, value):
        """
        Set constraint's before move happens active atoms data value.

        :Parameters:
            #. value (number): Data value.
        """
        self.__activeAtomsDataBeforeMove = value

    def set_active_atoms_data_after_move(self, value):
        """
        Set constraint's after move happens active atoms data value.

        :Parameters:
            #. value (number): data value.
        """
        self.__activeAtomsDataAfterMove = value

    def set_after_move_standard_error(self, value):
        """
        Set constraint's standard error value after move happens.

        :Parameters:
            #. value (number): standard error value.
        """
        self.__afterMoveStandardError = value

    def set_amputation_data(self, value):
        """
        Set constraint's after amputation data.

        :Parameters:
            #. value (number): data value.
        """
        self.__amputationData = value

    def set_amputation_standard_error(self, value):
        """
        Set constraint's standardError after amputation.

        :Parameters:
            #. value (number): standard error value.
        """
        self.__amputationStandardError = value

    def reset_constraint(self, reinitialize=True, flags=False, data=False):
        """
        Reset constraint.

        :Parameters:
            #. reinitialize (boolean): If set to True, it will override
               the rest of the flags and will completely reinitialize the
               constraint.
            #. flags (boolean): Reset the state, tried and accepted flags
               of the constraint.
            #. data (boolean): Reset the constraints computed data.
        """
        # reinitialize constraint
        if reinitialize:
            flags = False
            data  = False
            self.__initialize_constraint()
        # initialize flags
        if flags:
            self.__state                  = None
            self.__tried                  = 0
            self.__accepted               = 0
            self.__standardError          = None
            self.__afterMoveStandardError = None
            # dunp to repository
            self._dump_to_repository({'_Constraint__state'                  : self.__state,
                                      '_Constraint__tried'                  : self.__tried,
                                      '_Constraint__accepted'               : self.__accepted,
                                      '_Constraint__standardError'          : self.__standardError,
                                      '_Constraint__afterMoveStandardError' : self.__afterMoveStandardError})
        # initialize data
        if data:
            self.__originalData              = None
            self.__data                      = None
            self.__activeAtomsDataBeforeMove = None
            self.__activeAtomsDataAfterMove  = None
            self.__standardError             = None
            self.__afterMoveStandardError    = None
            # dunp to repository
            self._dump_to_repository({'_Constraint__originalData'             : self.__originalData,
                                      '_Constraint__data'                     : self.__data,
                                      '_Constraint__activeAtomsDataBeforeMove': self.__activeAtomsDataBeforeMove,
                                      '_Constraint__activeAtomsDataAfterMove' : self.__activeAtomsDataAfterMove,
                                      '_Constraint__standardError'            : self.__standardError,
                                      '_Constraint__afterMoveStandardError'   : self.__afterMoveStandardError})


    def compute_and_set_standard_error(self):
        """ Compute and set constraint's standard error by calling
        compute_standard_error method and passing constraint's data."""
        self.set_standard_error(self.compute_standard_error(data = self.data))

    def get_constraint_value(self):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def get_constraint_original_value(self):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def compute_standard_error(self):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def compute_data(self):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def compute_before_move(self, realIndexes, relativeIndexes):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def compute_after_move(self, realIndexes, relativeIndexes, movedBoxCoordinates):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def accept_move(self, realIndexes, relativeIndexes):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def reject_move(self, realIndexes, relativeIndexes):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def compute_as_if_amputated(self, realIndex, relativeIndex):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def compute_as_if_inserted(self, realIndex, relativeIndex):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def accept_amputation(self, realIndex, relativeIndex):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def reject_amputation(self, realIndex, relativeIndex):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def accept_insertion(self, realIndex, relativeIndex):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def reject_insertion(self, realIndex, relativeIndex):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def _on_collector_collect_atom(self, realIndex):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def _on_collector_release_atom(self, realIndex):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def _on_collector_reset(self):
        """Method must be overloaded in children classes."""
        raise Exception(LOGGER.impl("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def export(self, *args, **kwargs):
        """Method must be overloaded in children classes."""
        LOGGER.warn("%s export method is not implemented"%(self.__class__.__name__))

    def plot(self, *args, **kwargs):
        """Method must be overloaded in children classes."""
        LOGGER.warn("%s plot method is not implemented"%(self.__class__.__name__))


class ExperimentalConstraint(Constraint):
    """
    Experimental constraint is any constraint related to experimental data.

    :Parameters:
        #. engine (None, fullrmc.Engine): Constraint's stochastic engine.
        #. experimentalData (numpy.ndarray, string): Experimental data goiven
           as numpy.ndarray or string path to load data using numpy.loadtxt
           method.
        #. dataWeights (None, numpy.ndarray): Weights array of the same number
           of points of experimentalData used in the constraint's standard
           error computation. Therefore particular fitting emphasis can be
           put on different data points that might be considered as more or less
           important in order to get a reasonable and plausible modal.\n
           If None is given, all data points are considered of the same
           importance in the computation of the constraint's standard error.\n
           If numpy.ndarray is given, all weights must be positive and all
           zeros weighted data points won't contribute to the total
           constraint's standard error. At least a single weight point is
           required to be non-zeros and the weights array will be automatically
           scaled upon setting such as the the sum of all the weights
           is equal to the number of data points.
        #. scaleFactor (number): A normalization scale factor used to normalize
           the computed data to the experimental ones.
        #. adjustScaleFactor (list, tuple): Used to adjust fit or guess
           the best scale factor during stochastic engine runtime.
           It must be a list of exactly three entries.\n
           #. The frequency in number of generated moves of finding the best
              scale factor. If 0 frequency is given, it means that the scale
              factor is fixed.
           #. The minimum allowed scale factor value.
           #. The maximum allowed scale factor value.

    **NB**: If adjustScaleFactor first item (frequency) is 0, the scale factor
    will remain untouched and the limits minimum and maximum won't be checked.

    """
    def __init__(self, experimentalData, dataWeights=None, scaleFactor=1.0, adjustScaleFactor=(0, 0.8, 1.2) ):
        # initialize constraint
        super(ExperimentalConstraint, self).__init__()
        # set the constraint's experimental data
        self.__dataWeights      = None
        self.__experimentalData = None
        self.set_experimental_data(experimentalData)
        # set scale factor
        self.set_scale_factor(scaleFactor)
        # set adjust scale factor
        self.set_adjust_scale_factor(adjustScaleFactor)
        # set data weights
        self.set_data_weights(dataWeights)
        # set frame data
        FRAME_DATA = [d for d in self.FRAME_DATA]
        FRAME_DATA.extend(['_ExperimentalConstraint__dataWeights',
                           '_ExperimentalConstraint__experimentalData',
                           '_ExperimentalConstraint__scaleFactor'] )
        RUNTIME_DATA = [d for d in self.RUNTIME_DATA]
        RUNTIME_DATA.extend( ['_ExperimentalConstraint__scaleFactor'] )
        object.__setattr__(self, 'FRAME_DATA',  tuple(FRAME_DATA)   )
        object.__setattr__(self, 'RUNTIME_DATA',tuple(RUNTIME_DATA) )

    def _set_fitted_scale_factor_value(self, scaleFactor):
        """
        This method is a scaleFactor value without any validity checking.
        Meant to be used internally only.
        """
        if self.__scaleFactor != scaleFactor:
            LOGGER.info("Experimental constraint '%s' scale factor updated from %.6f to %.6f" %(self.__class__.__name__, self.__scaleFactor, scaleFactor))
            self.__scaleFactor = scaleFactor

    @property
    def experimentalData(self):
        """ Experimental data of the constraint. """
        return self.__experimentalData

    @property
    def dataWeights(self):
        """ Experimental data points weight"""
        return self.__dataWeights

    @property
    def scaleFactor(self):
        """ Constraint's scaleFactor. """
        return self.__scaleFactor

    @property
    def adjustScaleFactor(self):
        """Adjust scale factor tuple."""
        return (self.__adjustScaleFactorFrequency, self.__adjustScaleFactorMinimum, self.__adjustScaleFactorMaximum)

    @property
    def adjustScaleFactorFrequency(self):
        """ Scale factor adjustment frequency. """
        return self.__adjustScaleFactorFrequency

    @property
    def adjustScaleFactorMinimum(self):
        """ Scale factor adjustment minimum number allowed. """
        return self.__adjustScaleFactorMinimum

    @property
    def adjustScaleFactorMaximum(self):
        """ Scale factor adjustment maximum number allowed. """
        return self.__adjustScaleFactorMaximum

    def set_scale_factor(self, scaleFactor):
        """
        Set the scale factor.

        :Parameters:
             #. scaleFactor (number): A normalization scale factor used to
                normalize the computed data to the experimental ones.
        """
        assert is_number(scaleFactor), LOGGER.error("scaleFactor must be a number")
        self.__scaleFactor = FLOAT_TYPE(scaleFactor)
        # dump to repository
        self._dump_to_repository({'_ExperimentalConstraint__scaleFactor' :self.__scaleFactor})
        ## reset constraint
        self.reset_constraint()

    def set_adjust_scale_factor(self, adjustScaleFactor):
        """
        Set adjust scale factor.

        :Parameters:
            #. adjustScaleFactor (list, tuple): Used to adjust fit or guess
               the best scale factor during stochastic engine runtime.
               It must be a list of exactly three entries.\n
               #. The frequency in number of generated moves of finding the best
                  scale factor. If 0 frequency is given, it means that the scale
                  factor is fixed.
               #. The minimum allowed scale factor value.
               #. The maximum allowed scale factor value.
        """
        assert isinstance(adjustScaleFactor, (list, tuple)), LOGGER.error('adjustScaleFactor must be a list.')
        assert len(adjustScaleFactor) == 3, LOGGER.error('adjustScaleFactor must be a list of exactly three items.')
        freq  = adjustScaleFactor[0]
        minSF = adjustScaleFactor[1]
        maxSF = adjustScaleFactor[2]
        assert is_integer(freq), LOGGER.error("adjustScaleFactor first item (frequency) must be an integer.")
        freq = INT_TYPE(freq)
        assert freq>=0, LOGGER.error("adjustScaleFactor first (frequency) item must be bigger or equal to 0.")
        assert is_number(minSF), LOGGER.error("adjustScaleFactor second item (minimum) must be a number.")
        minSF = FLOAT_TYPE(minSF)
        assert is_number(maxSF), LOGGER.error("adjustScaleFactor third item (maximum) must be a number.")
        maxSF = FLOAT_TYPE(maxSF)
        assert minSF<=maxSF, LOGGER.error("adjustScaleFactor second item (minimum) must be smaller or equal to third second item (maximum).")
        # set values
        self.__adjustScaleFactorFrequency = freq
        self.__adjustScaleFactorMinimum   = minSF
        self.__adjustScaleFactorMaximum   = maxSF
        # dump to repository
        self._dump_to_repository({'_ExperimentalConstraint__adjustScaleFactorFrequency': self.__adjustScaleFactorFrequency,
                                  '_ExperimentalConstraint__adjustScaleFactorMinimum'  : self.__adjustScaleFactorMinimum,
                                  '_ExperimentalConstraint__adjustScaleFactorMaximum'  : self.__adjustScaleFactorMaximum})
        # reset constraint
        self.reset_constraint()

    def _set_adjust_scale_factor_frequency(self, freq):
        """This must never be used externally. It's added to serve RemoveGenerators
         and only used internally upon calling compute_as_if_amputated """
        self.__adjustScaleFactorFrequency = freq

    def set_experimental_data(self, experimentalData):
        """
        Set the constraint's experimental data.

        :Parameters:
            #. experimentalData (numpy.ndarray, string): Experimental data as
               numpy.ndarray or string path to load data using numpy.loadtxt
               method.
        """
        if isinstance(experimentalData, basestring):
            try:
                experimentalData = np.loadtxt(str(experimentalData), dtype=FLOAT_TYPE)
            except Exception as e:
                raise Exception(LOGGER.error("unable to load experimentalData path '%s' (%s)"%(experimentalData, e)))
        assert isinstance(experimentalData, np.ndarray), LOGGER.error("experimentalData must be a numpy.ndarray or string path to load data using numpy.loadtxt.")
        # check data format
        valid, message = self.check_experimental_data(experimentalData)
        # set experimental data
        if valid:
            self.__experimentalData = experimentalData
        else:
            raise Exception( LOGGER.error("%s"%message) )
        # dump to repository
        self._dump_to_repository({'_ExperimentalConstraint__experimentalData': self.__experimentalData})

    def set_data_weights(self, dataWeights):
        """
        Set experimental data points weight.

        :Parameters:
            #. dataWeights (None, numpy.ndarray): Weights array of the same
               number of points of experimentalData used in the constraint's
               standard error computation. Therefore particular fitting
               emphasis can be put on different data points that might be
               considered as more or less important in order to get a
               reasonable and plausible modal.\n
               If None is given, all data points are considered of the same
               importance in the computation of the constraint's standard error.\n
               If numpy.ndarray is given, all weights must be positive and all
               zeros weighted data points won't contribute to the total
               constraint's standard error. At least a single weight point is
               required to be non-zeros and the weights array will be
               automatically scaled upon setting such as the the sum of all
               the weights is equal to the number of data points.
        """
        if dataWeights is not None:
            assert isinstance(dataWeights, (list, tuple, np.ndarray)), LOGGER.error("dataWeights must be None or a numpy array of weights")
            try:
                dataWeights = np.array(dataWeights, dtype=FLOAT_TYPE)
            except Exception as e:
                raise Exception(LOGGER.error("unable to cast dataWeights as a numpy array (%s)"%(e)))
            assert len(dataWeights.shape) == 1, LOGGER.error("dataWeights must be a vector")
            assert len(dataWeights) == self.__experimentalData.shape[0], LOGGER.error("dataWeights must be a of the same length as experimental data")
            assert np.min(dataWeights) >=0, LOGGER.error("dataWeights negative values are not allowed")
            assert np.sum(dataWeights), LOGGER.error("dataWeights must be a non-zero array")
            dataWeights /= FLOAT_TYPE( np.sum(dataWeights) )
            dataWeights *= FLOAT_TYPE( len(dataWeights) )
        self.__dataWeights = dataWeights
        # dump to repository
        self._dump_to_repository({'_ExperimentalConstraint__dataWeights': self.__dataWeights})

    def check_experimental_data(self, experimentalData):
        """
        Checks the constraint's experimental data
        This method must be overloaded in all experimental constraint
        sub-classes.

        :Parameters:
            #. experimentalData (numpy.ndarray): Experimental data numpy.ndarray.
        """
        raise Exception(LOGGER.error("%s '%s' method must be overloaded"%(self.__class__.__name__,inspect.stack()[0][3])))

    def fit_scale_factor(self, experimentalData, modelData, dataWeights):
        """
        The best scale factor value is computed by minimizing :math:`E=sM`.\n

        Where:
            #. :math:`E` is the experimental data.
            #. :math:`s` is the scale factor.
            #. :math:`M` is the model constraint data.

        :Parameters:
            #. experimentalData (numpy.ndarray): Experimental data.
            #. modelData (numpy.ndarray): Constraint modal data.
            #. dataWeights (None, numpy.ndarray): Data points weights to
               compute the scale factor. If None is given, all data points
               will be considered as having the same weight.

        :Returns:
            #. scaleFactor (number): The new scale factor fit value.

        **NB**: This method won't update the internal scale factor value
        of the constraint. It always computes the best scale factor given
        some experimental and model data.
        """
        if dataWeights is None:
            SF = FLOAT_TYPE( np.sum(modelData*experimentalData)/np.sum(modelData**2) )
        else:
            SF = FLOAT_TYPE( np.sum(dataWeights*modelData*experimentalData)/np.sum(modelData**2) )
        SF = max(SF, self.__adjustScaleFactorMinimum)
        SF = min(SF, self.__adjustScaleFactorMaximum)
        return SF

    def get_adjusted_scale_factor(self, experimentalData, modelData, dataWeights):
        """
        Checks if scale factor should be updated according to the given scale
        factor frequency and engine's accepted steps. If adjustment is due,
        a new scale factor will be computed using fit_scale_factor method,
        otherwise the the constraint's scale factor will be returned.

        :Parameters:
            #. experimentalData (numpy.ndarray): the experimental data.
            #. modelData (numpy.ndarray): the constraint modal data.
            #. dataWeights (None, numpy.ndarray): the data points weights to
               compute the scale factor. If None is given, all data points
               will be considered as having the same weight.

        :Returns:
            #. scaleFactor (number): Constraint's scale factor or the
            new scale factor fit value.

        **NB**: This method WILL NOT UPDATE the internal scale factor
        value of the constraint.
        """
        SF = self.__scaleFactor
        # check to update scaleFactor
        if self.__adjustScaleFactorFrequency:
            if not self.engine.accepted%self.adjustScaleFactorFrequency:
                SF = self.fit_scale_factor(experimentalData, modelData, dataWeights)
        return SF

    def compute_standard_error(self, experimentalData, modelData):
        """
        Compute the squared deviation between modal computed data
        and the experimental ones.

        .. math::
            SD = \\sum \\limits_{i}^{N} W_{i}(Y(X_{i})-F(X_{i}))^{2}

        Where:\n
        :math:`N` is the total number of experimental data points. \n
        :math:`W_{i}` is the data point weight. It becomes equivalent to 1
        when dataWeights is set to None. \n
        :math:`Y(X_{i})` is the experimental data point :math:`X_{i}`. \n
        :math:`F(X_{i})` is the computed from the model data  :math:`X_{i}`. \n

        :Parameters:
            #. experimentalData (numpy.ndarray): Experimental data.
            #. modelData (numpy.ndarray): The data to compare with the
               experimental one and compute the squared deviation.

        :Returns:
            #. standardError (number): The calculated standard error of
               the constraint.
        """
        # compute difference
        diff = experimentalData-modelData
        # return squared deviation
        if self.__dataWeights is None:
            return np.add.reduce((diff)**2)
        else:
            return np.add.reduce(self.__dataWeights*(diff)**2)


class SingularConstraint(Constraint):
    """ A singular constraint is a constraint that doesn't allow multiple
    instances in the same engine."""

    def is_singular(self, engine):
        """
        Get whether only one instance of this constraint type is present
        in the stochastic engine. True for only itself found, False for
        other instance of the same __class__.__name__.
        """
        for c in engine.constraints:
            if c is self:
                continue
            if c.__class__.__name__ == self.__class__.__name__:
                return False
        return True

    def assert_singular(self, engine):
        """
        Checks whether only one instance of this constraint type is
        present in the stochastic engine. Raises Exception if multiple
        instances are present.
        """
        assert self.is_singular(engine), LOGGER.error("Only one instance of constraint '%s' is allowed in the same engine"%self.__class__.__name__)


class RigidConstraint(Constraint):
    """
    A rigid constraint is a constraint that doesn't count into the total
    standard error of the stochastic Engine. But it's internal standard error
    must monotonously decrease or remain the same from one engine step to
    another. If standard error of an rigid constraint increases the
    step will be rejected even before engine's new standardError get computed.

    :Parameters:
        #. engine (None, fullrmc.Engine): The constraint stochastic engine.
        #. rejectProbability (Number): Rejecting probability of all steps
           where standard error increases. It must be between 0 and 1 where
           1 means rejecting all steps where standardError increases
           and 0 means accepting all steps regardless whether standard error
           increases or not.
    """
    def __init__(self, rejectProbability):
        # initialize constraint
        super(RigidConstraint, self).__init__()
        # set probability
        self.set_reject_probability(rejectProbability)
        # set frame data
        FRAME_DATA = [d for d in self.FRAME_DATA]
        FRAME_DATA.extend(['_RigidConstraint__rejectProbability'] )
        object.__setattr__(self, 'FRAME_DATA',  tuple(FRAME_DATA) )

    @property
    def rejectProbability(self):
        """ Rejection probability. """
        return self.__rejectProbability

    def set_reject_probability(self, rejectProbability):
        """
        Set the rejection probability.

        :Parameters:
            #. rejectProbability (Number): rejecting probability of all steps
               where standard error increases. It must be between 0 and 1
               where 1 means rejecting all steps where standardError increases
               and 0 means accepting all steps regardless whether standard
               error increases or not.
        """
        assert is_number(rejectProbability), LOGGER.error("rejectProbability must be a number")
        rejectProbability = FLOAT_TYPE(rejectProbability)
        assert rejectProbability>=0 and rejectProbability<=1, LOGGER.error("rejectProbability must be between 0 and 1")
        self.__rejectProbability = rejectProbability
        # dump to repository
        self._dump_to_repository({'_RigidConstraint__dataWeights': self.__rejectProbability})

    def should_step_get_rejected(self, standardError):
        """
        Given a standard error, return whether to keep or reject new
        standard error according to the constraint reject probability.

        :Parameters:
            #. standardError (number): The standard error to compare with
            the Constraint standard error

        :Return:
            #. result (boolean): True to reject step, False to accept
        """
        if self.standardError is None:
            raise Exception(LOGGER.error("must compute data first"))
        if standardError<=self.standardError:
            return False
        return randfloat() < self.__rejectProbability

    def should_step_get_accepted(self, standardError):
        """
        Given a standard error, return whether to keep or reject new standard
        error according to the constraint reject probability.

        :Parameters:
            #. standardError (number): The standard error to compare with
               the Constraint standard error

        :Return:
            #. result (boolean): True to accept step, False to reject
        """
        return not self.should_step_get_reject(standardError)


class QuasiRigidConstraint(RigidConstraint):
    """
    A quasi-rigid constraint is a another rigid constraint but it becomes f
    ree above a certain threshold ratio of satisfied data. Every quasi-rigid
    constraint has its own definition of maximum standard error. The ratio is
    computed as between current standard error and maximum standard error.

     .. math::

        ratio = 1-\\frac{current\ standard\ error}{maximum\ standard\ error}

    :Parameters:
        #. engine (None, fullrmc.Engine): The constraint stochastic engine.
        #. rejectProbability (Number): Rejecting probability of all steps
           where standardError increases only before threshold ratio is reached.
           It must be between 0 and 1 where 1 means rejecting all steps where
           standardError increases and 0 means accepting all steps regardless
           whether standardError increases or not.
        #. thresholdRatio(Number): The threshold of satisfied data, above
           which the constraint become free. It must be between 0 and 1 where
           1 means all data must be satisfied and therefore the constraint
           behave like a RigidConstraint and 0 means none of the data must be
           satisfied and therefore the constraint becomes always free and
           useless.
    """
    def __init__(self, engine, rejectProbability, thresholdRatio):
        # initialize constraint
        super(QuasiRigidConstraint, self).__init__(engine=engine, rejectProbability=rejectProbability)
        # set probability
        self.set_threshold_ratio(thresholdRatio)
        # initialize maximum standard error
        #self.__maximumStandardError = None
        self._set_maximum_standard_error(None)
        # set frame data
        FRAME_DATA = [d for d in self.FRAME_DATA]
        FRAME_DATA.extend(['_QuasiRigidConstraint__thresholdRatio',
                           '_QuasiRigidConstraint__maximumStandardError'] )
        object.__setattr__(self, 'FRAME_DATA',  tuple(FRAME_DATA) )


    def _set_maximum_standard_error(self, maximumStandardError):
        """ Set the maximum standard error. Use carefully, it's not meant to
        be used externally. maximum squared deviation is what is used to
        compute the ratio and compare to threshold ratio.
        """
        if (maximumStandardError is not None) and maximumStandardError:
            assert is_number(maximumStandardError), LOGGER.error("maximumStandardError must be a number.")
            maximumStandardError = FLOAT_TYPE(maximumStandardError)
            assert maximumStandardError>0, LOGGER.error("maximumStandardError must be a positive.")
        self.__maximumStandardError = maximumStandardError
        # dump to repository
        self._dump_to_repository({'_QuasiRigidConstraint__maximumStandardError': self.__maximumStandardError})

    @property
    def thresholdRatio(self):
        """ Threshold ratio. """
        return self.__thresholdRatio

    @property
    def currentRatio(self):
        return 1-(self.standardError/self.__maximumStandardError)

    def set_threshold_ratio(self, thresholdRatio):
        """
        Set the rejection probability function.

        :Parameters:
            #. thresholdRatio(Number): The threshold of satisfied data, above
               which the constraint become free. It must be between 0 and 1
               where 1 means all data must be satisfied and therefore the
               constraint behave like a RigidConstraint and 0 means none of
               the data must be satisfied and therefore the constraint
               becomes always free and useless.
        """
        assert is_number(thresholdRatio), LOGGER.error("thresholdRatio must be a number")
        thresholdRatio = FLOAT_TYPE(thresholdRatio)
        assert thresholdRatio>=0 and thresholdRatio<=1, LOGGER.error("thresholdRatio must be between 0 and 1")
        self.__thresholdRatio = thresholdRatio
        # dump to repository
        self._dump_to_repository({'_QuasiRigidConstraint__thresholdRatio': self.__thresholdRatio})

    def should_step_get_rejected(self, standardError):
        """
        Given a standard error, return whether to keep or reject new
        standard error according to the constraint reject probability function.

        :Parameters:
            #. standardError (number): Standard error to compare with the
            Constraint standard error.

        :Return:
            #. result (boolean): True to reject step, False to accept.
        """
        previousRatio = 1-(self.standardError/self.__maximumStandardError)
        currentRatio  = 1-(standardError/self.__maximumStandardError)
        if currentRatio>=self.__thresholdRatio: # must be accepted
            return False
        elif previousRatio>=self.__thresholdRatio: # it must be rejected
            return randfloat() < self.rejectProbability
        elif standardError<=self.standardError: # must be accepted
            return False
        else: # must be rejected
            return randfloat() < self.rejectProbability
