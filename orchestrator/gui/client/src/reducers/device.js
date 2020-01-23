import * as actuator from '../actions/actuator'
import * as device from '../actions/device'

import {
  checkSchema,
  mergeByProperty
} from '../components/utils'

const initialState = {
  devices: [],
  sort: '',
  count: 0,
  errors: {}
}

export default (state=initialState, action=null) => {
  let tmpState = {}
  let devices = []

  switch(action.type) {
    case device.GET_DEVICES_SUCCESS:
      let newDevs = action.payload.results || []
      devices = action.meta.refresh ? newDevs : mergeByProperty(state.devices, newDevs, 'device_id')

      return {
        ...state,
        count: action.payload.count || 0,
        devices: devices.map((dev, i) => ({ ...dev, schema: checkSchema(dev.schema || {})})),
        sort: action.meta.sort,
        errors: {
          ...state.errors,
          [device.GET_DEVICES_FAILURE]: {}
        }
      }

    case device.CREATE_DEVICE_SUCCESS:
      setTimeout(() => {
        action.asyncDispatch(device.getDevices({page: 1, count: state.devices.length+1, sort: state.sort, refresh: true}))
      }, 500)

      return {
        ...state,
        errors: {
          ...state.errors,
          [device.CREATE_DEVICE_FAILURE]: {}
        }
      }

    case device.GET_DEVICE_SUCCESS:
      let newDev = [action.payload] || []
      devices = mergeByProperty(state.devices, newDev, 'device_id')

      return {
        ...state,
        devices: devices.map((dev, i) => ({ ...dev, schema: checkSchema(dev.schema || {})})),
        errors: {
          ...state.errors,
          [device.GET_DEVICE_FAILURE]: {}
        }
      }

    case device.UPDATE_DEVICE_SUCCESS:
      setTimeout(() => {
        action.asyncDispatch(device.getDevices({page: 1, count: state.devices.length, sort: state.sort, refresh: true}))
      }, 500)

      return {
        ...state,
        errors: {
          ...state.errors,
          [device.UPDATE_DEVICE_FAILURE]: {}
        }
      }

    case device.DELETE_DEVICE_SUCCESS:
      setTimeout(() => {
        action.asyncDispatch(device.getDevices({page: 1, count: state.devices.length, sort: state.sort, refresh: true}))
        action.asyncDispatch(actuator.getActuators({refresh: true}))
      }, 500)

      return {
        ...state,
        errors: {
          ...state.errors,
          [device.DELETE_DEVICE_FAILURE]: {}
        }
      }

    case device.GET_DEVICE_USERS_SUCCESS:
      console.log(action.payload)
      return {
        ...state,
        errors: {
          ...state.errors,
          [device.GET_DEVICE_USERS_FAILURE]: {}
        }
      }

    case device.GET_DEVICES_FAILURE:
    case device.CREATE_DEVICE_FAILURE:
    case device.GET_DEVICE_FAILURE:
    case device.UPDATE_DEVICE_FAILURE:
    case device.DELETE_DEVICE_FAILURE:
    case device.GET_DEVICE_USERS_FAILURE:
      console.log('Device Failure', action.type, action)
      return {
        ...state,
        errors: {
          ...state.errors,
          [action.type]: action.payload.response || {'non_field_errors': action.payload.statusText},
        }
      }

    default:
      return state
  }
}