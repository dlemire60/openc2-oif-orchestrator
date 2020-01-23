import React, { Component } from 'react'
import { connect } from 'react-redux'
import PropTypes from 'prop-types'

import JSONPretty from 'react-json-pretty'

import {
  Button,
  Form,
  FormGroup,
  FormText,
  Input,
  Label
} from 'reactstrap'

import Array from './array'
import Basic from './basicField'
import Choice from './choice'
import Enumerated from './enumerated'
import Map from './map'
import Record from './record'

import {
  isOptional_json,
  opts2arr,
} from '../'

import { safeGet } from '../../../../../utils'


class Field extends Component {
  render() {
    let def = { ...this.props.def }

    if (def.hasOwnProperty("$ref")) {
      let ref_name = def["$ref"].replace(/^#\/definitions\//, "")
      delete def["$ref"]

      def = {
        ...this.props.schema.definitions[ref_name],
        ...def
      }
    }

    let fieldArgs = {
      root: this.props.root,
      parent: this.props.parent,
      name: this.props.name || def.name,
      def: def,
      required: this.props.required,
      optChange: (k, v) => this.props.optChange(k, v, this.props.idx)
    }

    // console.log(this.props.name || def.name, def)
    switch(def.type) {
      case "object":
        let min_props = safeGet(def, "minProperties")
        let max_props = safeGet(def, "maxProperties")
        if (min_props == 1 && max_props == 1) {
          // console.log("Choice - " + fieldArgs.name + ", min: "+ min_props + ", max: " + max_props)
          // return <p><strong>Choice</strong>: { this.props.name }</p>
          return <Choice { ...fieldArgs } />

        } else if (min_props >= 1 && max_props == null) {
          // console.log("Map - " + fieldArgs.name + ", min: "+ min_props + ", max: " + max_props)
          // return <p><strong>Map</strong>: { this.props.name }</p>
          return <Map { ...fieldArgs } />

        } else if (def.hasOwnProperty('properties') || (min_props == null && max_props == null)) {
          // console.log("Record - " + fieldArgs.name + ", min: "+ min_props + ", max: " + max_props)
          // return <p><strong>Record</strong>: { this.props.name }</p>
          return <Record { ...fieldArgs } />
        }
        return <p><strong>Object</strong>: { this.props.name }</p>
      case 'array':
        // console.log("Array - " + fieldArgs.name)
        // return <p><strong>Array</strong>: { this.props.name }</p>
        return <Array { ...fieldArgs } />
      default:
        if (def.hasOwnProperty('enum') || def.hasOwnProperty("oneOf")) {
          // console.log("Enum - " + fieldArgs.name)
          // return <p><strong>Enumerated</strong>: { this.props.name }</p>
          return <Enumerated { ...fieldArgs } />
        }
        // console.log("Basic - " + fieldArgs.name)
        // return <p><strong>Basic</strong>: { this.props.name }</p>
        return <Basic { ...fieldArgs } />
     }
  }
}

const mapStateToProps = (state) => ({
  schema: state.Generate.selectedSchema
})

const connectedField = connect(mapStateToProps)(Field)

connectedField.propTypes = {
  idx: PropTypes.number,
  parent: PropTypes.string,
  name: PropTypes.string,
  def: PropTypes.object,
  required: PropTypes.bool,
  optChange: PropTypes.func
}

connectedField.defaultProps = {
  idx: null,
  root: false,
  name: "Field",
  parent: "",
  def: {},
  required: false,
  optChange: (k, v) => console.log(k, v)
}

export {
  connectedField as default,
  connectedField as Field,
  isOptional_json
}

