console.log(widgetContext)
let $injector = widgetContext.$scope.$injector;
let customDialog = $injector.get(widgetContext.servicesMap.get('customDialog'));
let assetService = $injector.get(widgetContext.servicesMap.get('assetService'));
let deviceService = $injector.get(widgetContext.servicesMap.get('deviceService'));
let attributeService = $injector.get(widgetContext.servicesMap.get('attributeService'));
let entityRelationService = $injector.get(widgetContext.servicesMap.get('entityRelationService'));
// let edgeService = $injector.get(widgetContext.servicesMap.get('edgeService'));
// console.log("edgeService: ",edgeService)
openAddEntityDialog();

function openAddEntityDialog() {
    customDialog.customDialog(htmlTemplate, AddEntityDialogController).subscribe();
}

function AddEntityDialogController(instance) {
    let vm = instance;

    vm.wb_x_system_types = ["WB-X-924"];

    vm.addEntityFormGroup = vm.fb.group({
     wb_x_system_type: [null, [vm.validators.required]],
    });

    vm.labelDisplayFn=function(option) {
        if(option!=undefined){
            return option;
        }
        return ""
    }
    vm.filteredWBXSystemTypes = vm.wb_x_system_types;
    vm.filterWBXSystemTypes=function(value) {
        if(value!=undefined){
            const filterValue = value.toLowerCase();
            vm.filteredWBXSystemTypes = vm.wb_x_system_types.filter(type => type.toLowerCase().includes(filterValue));
        }
        else{
            vm.filteredWBXSystemTypes = vm.wb_x_system_types;
        }
    }


    vm.cancel = function() {
        vm.dialogRef.close(null);
    };
    function intToFourDigitString(number) {
      // Convert the number to a string
      let str = number.toString();
    
      // Calculate the number of leading zeros needed
      const leadingZeros = 4 - str.length;
    
      // Add leading zeros to the string
      if (leadingZeros > 0) {
        str = '0'.repeat(leadingZeros) + str;
      }
    
      return str;
    }

    vm.save = function() {
//                         console.log(guid(),generateSecret(20))
// return
        vm.addEntityFormGroup.markAsPristine();
        widgetContext.rxjs.forkJoin([widgetContext.entityService.findEntityDataByQuery({
  "entityFilter": {
    "type": "assetType",
    "resolveMultiple": true,
    "assetType": "WB-X-Systems"
  },
  "entityFields": [{
  "type": "ENTITY_FIELD",
  "key": "name"}  
],
  "keyFilters": [
	{"key":{"type":"ENTITY_FIELD","key":"name"},"valueType":"STRING","predicate":{"operation":"STARTS_WITH","value":{"defaultValue":vm.addEntityFormGroup.value.wb_x_system_type,"dynamicValue":null},"type":"STRING"}}  ],
  "latestValues": [],
  "pageLink": {
    "dynamic": true,
    "page": 0,
    "pageSize": 1,
    "sortOrder": {
      "direction": "DESC",
      "key": {
        "key": "createdTime",
        "type": "ENTITY_FIELD"
      }
    },
    "textSearch": ""
  }
}),
widgetContext.entityService.findEntityDataByQuery({
  "entityFilter": {
    "type": "deviceType",
    "resolveMultiple": true,
    "deviceType": "WB-X-SPS-X86_V1.0"
  },
  "entityFields": [{
  "type": "ENTITY_FIELD",
  "key": "name"}  
],
  "keyFilters": [],
  "latestValues": [],
  "pageLink": {
    "dynamic": true,
    "page": 0,
    "pageSize": 1,
    "sortOrder": {
      "direction": "DESC",
      "key": {
        "key": "createdTime",
        "type": "ENTITY_FIELD"
      }
    },
    "textSearch": ""
  }
}),
widgetContext.entityService.findEntityDataByQuery({
  "entityFilter": {
    "type": "deviceType",
    "resolveMultiple": true,
    "deviceType": "WB-X-CO2-ST-ESP32S3_V1.0"
  },
  "entityFields": [{
  "type": "ENTITY_FIELD",
  "key": "name"}  
],
  "keyFilters": [],
  "latestValues": [],
  "pageLink": {
    "dynamic": true,
    "page": 0,
    "pageSize": 1,
    "sortOrder": {
      "direction": "DESC",
      "key": {
        "key": "createdTime",
        "type": "ENTITY_FIELD"
      }
    },
    "textSearch": ""
  }
}),
widgetContext.entityService.findEntityDataByQuery({
  "entityFilter": {
    "type": "deviceType",
    "resolveMultiple": true,
    "deviceType": "WB-X-GATE_X86_V1.0"
  },
  "entityFields": [{
  "type": "ENTITY_FIELD",
  "key": "name"}  
],
  "keyFilters": [],
  "latestValues": [],
  "pageLink": {
    "dynamic": true,
    "page": 0,
    "pageSize": 1,
    "sortOrder": {
      "direction": "DESC",
      "key": {
        "key": "createdTime",
        "type": "ENTITY_FIELD"
      }
    },
    "textSearch": ""
  }
}),
widgetContext.entityService.findEntityDataByQuery({
  "entityFilter": {
    "type": "edgeType",
    "resolveMultiple": true,
    "edgeType": "WB-X-EDGE-X86_V1.0"
  },
  "entityFields": [{
  "type": "ENTITY_FIELD",
  "key": "name"}  
],
  "keyFilters": [],
  "latestValues": [],
  "pageLink": {
    "dynamic": true,
    "page": 0,
    "pageSize": 1,
    "sortOrder": {
      "direction": "DESC",
      "key": {
        "key": "createdTime",
        "type": "ENTITY_FIELD"
      }
    },
    "textSearch": ""
  }
})

]).subscribe(
            function (result) {
                console.log("Result: ",result)
                var _assetName;
                var _spsName;
                var _co2Name;
                var _gateName;
                var _edgeName;
                
                
                if(result[0].data.length==0){
                    _assetName=vm.addEntityFormGroup.value.wb_x_system_type+"_0001"
                }
                else{
                    var nameArray=result[0].data[0].latest.ENTITY_FIELD.name.value.split("_")
                    var lastIndex=parseInt(nameArray[nameArray.length - 1]);
                    _assetName=vm.addEntityFormGroup.value.wb_x_system_type+"_"+intToFourDigitString(lastIndex+1)
                }

                var spsNameArray=result[1].data[0].latest.ENTITY_FIELD.name.value.split("_")
                var spsLastIndex=parseInt(spsNameArray[spsNameArray.length - 1]);
                _spsName="WB-X-SPS_"+intToFourDigitString(spsLastIndex+1)

                var co2NameArray=result[2].data[0].latest.ENTITY_FIELD.name.value.split("_")
                var co2LastIndex=parseInt(co2NameArray[co2NameArray.length - 1]);
                _co2Name="WB-X-CO2_"+intToFourDigitString(co2LastIndex+1)


                var gateNameArray=result[3].data[0].latest.ENTITY_FIELD.name.value.split("_")
                var gateLastIndex=parseInt(gateNameArray[gateNameArray.length - 1]);
                _gateName="WB-X-GATE_"+intToFourDigitString(gateLastIndex+1)

                var edgeNameArray=result[4].data[0].latest.ENTITY_FIELD.name.value.split("_")
                var edgeLastIndex=parseInt(edgeNameArray[edgeNameArray.length - 1]);
                _edgeName="WB-X-EDGE_"+intToFourDigitString(edgeLastIndex+1)

                
                
    
                console.log(_assetName,_spsName,_co2Name,_gateName,_edgeName)
                
                
            widgetContext.rxjs.forkJoin([assetService.saveAsset({name: _assetName,type: "WB-X-Systems",label: _assetName}),
            deviceService.saveDevice({name: _spsName,type: "WB-X-SPS-X86_V1.0",label: _spsName}),
            deviceService.saveDevice({name: _co2Name,type: "WB-X-CO2-ST-ESP32S3_V1.0",label: _spsName}),
            deviceService.saveDevice({name: _gateName,type: "WB-X-GATE_X86_V1.0",label: _spsName}),
            widgetContext.entityService.edgeService.saveEdge({name: _edgeName,type: "WB-X-EDGE-X86_V1.0",label: _edgeName
                ,routingKey: guid()
                ,secret: generateSecret(20) 
            })
           
            ]).subscribe(function(savedEntities){
                
            console.log("savedEntities: ",savedEntities)
            widgetContext.rxjs.forkJoin([                
                entityRelationService.saveRelation({type:"HaveSPS",typeGroup:"COMMON",from:savedEntities[0].id,to:savedEntities[1].id}),
                entityRelationService.saveRelation({type:"HaveCO2",typeGroup:"COMMON",from:savedEntities[0].id,to:savedEntities[2].id}),
                entityRelationService.saveRelation({type:"HaveGATE",typeGroup:"COMMON",from:savedEntities[0].id,to:savedEntities[3].id}),
                entityRelationService.saveRelation({type:"Contains",typeGroup:"COMMON",from:savedEntities[4].id,to:savedEntities[0].id}),
                // entityRelationService.saveRelation({type:"HaveEdge",typeGroup:"COMMON",from:savedEntities[0].id,to:savedEntities[4].id}),
                widgetContext.http.post("/api/edge/"+savedEntities[4].id.id+"/device/"+savedEntities[1].id.id),
                widgetContext.http.post("/api/edge/"+savedEntities[4].id.id+"/device/"+savedEntities[2].id.id),
                widgetContext.http.post("/api/edge/"+savedEntities[4].id.id+"/device/"+savedEntities[3].id.id),
                widgetContext.http.post("/api/edge/"+savedEntities[4].id.id+"/asset/"+savedEntities[0].id.id)
                
            ]).subscribe(function(relationsResult){

            widgetContext.rxjs.forkJoin([                
                attributeService.saveEntityAttributes(savedEntities[1].id,"SHARED_SCOPE",_spsDefaultServerAttributes),
                attributeService.saveEntityAttributes(savedEntities[2].id,"SHARED_SCOPE",_co2DefaultSharedAttributes),
            ]).subscribe(function(attributeResult){

                widgetContext.updateAliases();
                vm.dialogRef.close(null);
                    
                })
                })

                })

            }
        );
    };


    var _co2DefaultSharedAttributes=[
    {
        "key": "heatingRelay",
        "value": true
    },
    {
        "key": "co2Relay",
        "value": true
    },
    {
        "key": "pumpRelais",
        "value": false
    },
    {
        "key": "isBackupController",
        "value": false
    },
    {
        "key": "swPressMaster",
        "value": 1.5
    }
]
    var _spsDefaultServerAttributes=[
    {
        "key": "ph_high_delay_duration",
        "value": 600
    },
    {
        "key": "radarSensorActive",
        "value": false
    },
    {
        "key": "powerButton",
        "value": true
    },
    {
        "key": "targetPHtolerrance",
        "value": 1.1
    },
    {
        "key": "calibratePH",
        "value": false
    },
    {
        "key": "callGpsSwitch",
        "value": false
    },
    {
        "key": "ph_low_delay_duration",
        "value": 60
    },
    {
        "key": "checkStatus",
        "value": false
    },
    {
        "key": "targetPHValue",
        "value": 7.6
    },
    {
        "key": "gemessener_low_wert",
        "value": 7
    },
    {
        "key": "get",
        "value": false
    },
    {
        "key": "co2HeatingRelaySw",
        "value": false
    },
    {
        "key": "getValue",
        "value": false
    },
    {
        "key": "turbiditySensorActive",
        "value": false
    },
    {
        "key": "co2RelaisSw",
        "value": false
    },
    {
        "key": "autoSwitch",
        "value": false
    },
    {
        "key": "gemessener_high_wert",
        "value": 10
    },
    {
        "key": "pumpRelaySw",
        "value": false
    },
    {
        "key": "pumpRelaySwSig",
        "value": false
    }
]

    function guid(){
      function s4(){
        return Math.floor((1 + Math.random()) * 0x10000)
          .toString(16)
          .substring(1);
      }
      return s4() + s4() + '-' + s4() + '-' + s4() + '-' +
        s4() + '-' + s4() + s4() + s4();
    }
    function generateSecret(length){
      if (length==undefined || length == null) {
        length = 1;
      }
      const l = length > 10 ? 10 : length;
      const str = Math.random().toString(36).substr(2, l);
      if (str.length >= length) {
        return str;
      }
      return str.concat(generateSecret(length - str.length));
    }
}
