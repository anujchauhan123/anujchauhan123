import React, { useState, useEffect } from "react";
import * as Device from "expo-device";
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Image,
  ImageBackground,
  StatusBar,
  TouchableOpacity,
  LogBox,
  Dimensions,
  ActivityIndicator,
  Pressable
} from "react-native";
// import CheckBox from '@react-native-community/checkbox';
import CheckBox from 'react-native-check-box';
import DropDownPicker from 'react-native-dropdown-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from "axios";
import Modal from 'react-native-modal';
import FontAwesome5Icon from "@expo/vector-icons/FontAwesome5";
import { Input, Button } from "react-native-elements";
import * as SecureStore from "expo-secure-store";
import { ScrollView } from "react-native-gesture-handler";
import PasswordInputText from 'react-native-hide-show-password-input';
// import { AsyncStorage } from 'react-native';
import AppLoading from 'expo-app-loading';
import {widthPercentageToDP as wp, heightPercentageToDP as hp} from 'react-native-responsive-screen';
import { LinearGradient } from 'expo-linear-gradient';

LogBox.ignoreLogs([
  "It appears that you are using old version of react-navigation library",
]);

const { width } = Dimensions.get("window");
const { height } = Dimensions.get("window");

const Login = ({ navigation }) => {
  const [values, setValues] = useState({
    //url: "https://drwise.o2btechnologies.com",
    //username: "demo",
    //password: "demo",
    url: "http://3.111.112.153:8071",
    username: "",
    password: "",
  });
  // AsyncStorage.getItem('username').then((value) => this.setState({ 'username': values.username }))
  const [isLoading, setIsLoading] = useState(false);
  const [emailError, setEmailError] = useState("");
  const [demoEmail, setDemoEmail] = useState("");
  const image = "../../assets/a_CRM.png";
  const [error, setError] = useState("");
  var [isSelected, setSelection] = useState(false);
  const [stop, setStop] = useState(false);
  const [show_view, set_show_view] = useState(false);
  const [isModalVisible, setModalVisible] = useState(false);
  const [isModalVisible_two, setModalVisibleTwo] = useState(false);
  const [selected_db, setDB] = useState("");
  const [auto_login, setAutoLogin] = useState(false);
  // const [data_url, setData_url] = useState("");
  var auto = false;

 const _retrieveData = async () => {

  //console.log("I am inside retrieveData method")
  try {
      values.username = await AsyncStorage.getItem('username');
      values.password = await AsyncStorage.getItem('password');
      //console.log("values.username******",values.username);
      //console.log("values.password******",values.password)
      try{
          if (values.username && values.password){
            set_show_view(true);
            setAutoLogin(true);
            auto = true
            //console.log("auto_login************",auto_login);
            //console.log("I am inside if*************");
            fetchDbName(values.url); 
          }
        }
      catch (error){
        //console.log("errror********",error);
      }
    }
  catch (error) {

    //console.log("I am inside catch ++++++++++++++++++++++")
    AsyncStorage.getAllKeys((err, keys) => {
      AsyncStorage.multiGet(keys, (err, stores) => {
        stores.map((result, i, store) => {
          // get at each store's key/value so you can work with it
          if(store[i][0] === "url"){
            values.url = store[i][1];

          }
          if(store[i][0] === "username"){
            values.username = store[i][1];
          }
          if(store[i][0] === "password"){
            values.password = store[i][1];
          }      
          });
        });
      });
    // Error retrieving data
  }
};

  const toggleModalVisibility = () => {
    //console.log("Hello Hello!")
    setModalVisible(!isModalVisible);
  };

  const toggleModalVisibilityTwo = () => {
    //console.log("Hello Hello!");
    setEmailError("");
    setDemoEmail("");
    setModalVisibleTwo(!isModalVisible_two);
  };

  const fetchDbName1 = async(urlvalue) => {
    setModalVisible(true);

  };

  const requestDemo = async(urlvalue) => {
    //setModalVisible(true);
    setModalVisibleTwo(true);

  };


  const hit_go = () => {
    // console.log("Button hitted")
    // console.log("selected_db********",selected_db);
    // var dct1 = {
    //   'dbvalue' : selected_db,
    //   'data_url' : data_url,
    //   'username' : values.username.trim(),
    //   'password' : values.password
    // }
    // handleLogin(dct1);

  };

  const hit_go_demo = () => {
    var emailValid = false;
    if(demoEmail.length == 0){
        setEmailError("**Email is required!");
    }        
    else if(demoEmail.length < 6){
        setEmailError("**Email should be minimum 6 characters!");
    }      
    else if(demoEmail.indexOf(' ') >= 0){        
        setEmailError('**Email cannot contain spaces!');                          
    }    
    else{
        setEmailError("");
        emailValid = true;

        var url1 = 'http://3.111.112.153:8071/demo/details'
        axios
        .get(url1,
          {
          params: {
            email : demoEmail.trim().toLowerCase(),
          },
          })
          .then((response) => {
            //console.log("response.data.demo_url************",response.data.demo_url);
            //console.log("response.data.demo_url_database************",response.data.demo_url_database);
            //console.log("response.data.error************",response.data.error);
            if(!response.data.error){
              //console.log('EveryThing fine');
              var values1 = {
                'url' : response.data.demo_url,
                'username': demoEmail.trim().toLowerCase(),
                'password': '1234'
              }
              navigation.navigate("Home", { values : values1, database: response.data.demo_url_database });

            }
            else if(response.data.error && (!response.data.membership)){
              setEmailError("**You are not our member yet! Kindly create account first.");
              //console.log('You are not our member yet! Kindly create account first.');
            }
            else if(response.data.error && ((!response.data.demo_url) || (!response.data.demo_url_database))){
              setEmailError("**Technical fault found! Kindly contact to administrator.");
              //console.log('Technical fault found! Kindly contact to administrator.');
            }
            else{
              setEmailError("**Some error occured! Kindly contact to administrator.");
              //console.log('Some error occured! Kindly contact to administrator.');
            }
            //console.log("response_data*************",response);
          })      
          .catch((e) => { 
            //console.log("e***********",e);
            alert("Something Went Wrong! "+e);
          });

    }





    // console.log("Test************",demoEmail);
    // var values1 = {
    //   'url' : 'odoo15.o2btechnologies.com',
    //   'username': demoEmail,
    //   'password': '1234'
    // }
    // navigation.navigate("Home", { values : values1, database: "odoo15appsnew" });
  };

  const move_to_create_account_page = () => {


    toggleModalVisibilityTwo();
    navigation.navigate("Demo");
  };

  const fetchDbName = async(urlvalue) => {
  setIsLoading(true);
    if (values.username && values.password){
    // console.log("urlvalue@@@@@@@@@@");
    //   var url1 = 'https://ri-fx.erp.techtime.me/membership/login/details/odoo/mobile'
    //   axios
    //   .get(url1,
    //     {
    //     params: {
    //       email : values.username.trim().toLowerCase(),
    //     },
    //     })
    //     .then((response) => {
            // const data_url = response.data.db_url;
            //setData_url(response.data.db_url);
           //console.log("response.data.app_id*************",response.data);
            // if (response.data.membership == 1){
            //   if (response.data.expired == 0){
            //     if (response.data.draft == 0){

                  axios
                    .post(`http://3.111.112.153:8071/web/database/list`, {
                      params: {
                        pass: "supervisor351",
                      },
                    })
                    .then((response) => {
                      console.log("data_url************",response.data[0]);
                      //console.log("databasefor result",response.data);
                      //console.log("databasefor demourl@@@@@@@@@123",response.data.result);
                      //console.log("databasefor demourl@@@@@@@@@",response.data.result[0]);
                      // let database_array_length = response.data.result.length;
                      // console.log("database_array_length*******",database_array_length);
                      var dbvalue = response.data[0];
                      var dct = {
                        'dbvalue' : dbvalue,
                        'data_url' : '3.111.112.153:8071',
                        'username' : values.username,
                        'password' : values.password
                      }
                      console.log("dct@@@@@@@@@@@@@@@",dct)
                      handleLogin(dct);


                      // if (database_array_length > 1){
                      //   // fetchDbName1();
                      //   var dbvalue = response.data.result[0];
                      //   var dct = {
                      //     'dbvalue' : dbvalue,
                      //     'data_url' : data_url,
                      //     'username' : values.username.trim(),
                      //     'password' : values.password
                      //   }
                      //   handleLogin(dct);
                      // }else{
                      //   var dbvalue = response.data.result[0];
                      //   var dct = {
                      //     'dbvalue' : dbvalue,
                      //     'data_url' : data_url,
                      //     'username' : values.username.trim(),
                      //     'password' : values.password
                      //   }
                      //   handleLogin(dct);
                      // }
                    })
                    .catch((e) => {
                      console.log("eeeeeeeeeeeeeeeeeeeee",e)
                      setIsLoading(false);
                      alert("Invalid Crendentials!");
                    });
              //   }
              //   else if (response.data.draft == 1){
              //     setIsLoading(false);
              //     alert("Please Contact Support !");

              //   }  
              // }
            // else if(response.data.expired == 1){
            //   setIsLoading(false);
            //   alert("Membership Expired ! Please Pay on time. ");    
            // }


            // }
            // else if(response.data.membership == 0){
            //   setIsLoading(false);
            //   alert("Your subscription is not valid");    
            // }
            // else{
            //   setIsLoading(false);
            //   alert("Your subscription having Some Issues!");
            // }            
        // })
        // .catch((e) => {
        //   alert("Kindly Signup!")
        // setIsLoading(false);
        // });
      }
       else{
        if(!stop){
          //console.log("stop******",stop);
          alert("please enter valid credential!");
          setIsLoading(false);
        }
       }

};

  const handleLogin = (dct) => {
    //console.log("data_url@@@@@@@@@@@",dct);
    const url = `http://${dct.data_url}/web/session/authenticate`;
    // console.log("dct.dbvalue***********",dct.dbvalue);
    // console.log("dct.username***********",dct.username);
    // console.log("dct.password***********",dct.password);
    console.log("data_url1111@@@@@@@@@@@88888888888888888",url);
    fetch(url, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        params: {
          db : dct.dbvalue,
          login: dct.username,
          password: dct.password,
        },
      }),
    })
      .then((res) => res.json())
      .then(async (data) => {
        console.log("data.result.db*****",data.db);



        if (data.db == dct.dbvalue) {
          setIsLoading(false);
          //console.log("dct.dbvalue@@@@@@@",dct.dbvalue);
          var values1 = {
            'url' : dct.data_url,
            'username': dct.username,
            'password': dct.password
          }
          AsyncStorage.setItem('username', dct.username);
          AsyncStorage.setItem('password', dct.password);
          //console.log("values1@@@@@@@@@@@@@",values1,dct.dbvalue)
          navigation.navigate("Home", { values : values1, database: dct.dbvalue });
        } else {
          setIsLoading(false);
        }
      })
      .catch((e) => {
        setIsLoading(false);
        console.log("auto login check************",e);
        //console.log("auto*********************",auto);
        if (auto){
          //console.log("auto login check************");
          set_show_view(false);
          //navigation.navigate("Demo");
        }
        alert("Kindly enter the correct credentials !")
      });
  };

  const [isReady, setIsReady] = React.useState(false);
  if (!isReady) {
    return (
      <AppLoading
        startAsync={_retrieveData}
        onFinish={() => setIsReady(true)}
        onError={console.warn}
      />
    );
  }

  return (

    show_view

    ?

    <View
      style={{
        flex: 1,
        backgroundColor: "#84563f",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
    <StatusBar backgroundColor={"#84563f"} barStyle="light-content"></StatusBar>
      <Image source={require(image)} style={{ height: 240, width: 240 }} />
      <ActivityIndicator color="#84563f" size="large" style={{ marginTop: 10 }} />
    </View>

    :

    <View style={styles.container}>
      <ImageBackground source={require("../../assets/pexels-photo.jpeg")}
        style={{ height: hp('100%') }}>
      <StatusBar backgroundColor={"#84563f"} barStyle="light-content"></StatusBar>
      <ScrollView>


      
        <View style={{ flex: 1 }}>
          <View
            style={{
              flex: 1,
            }}
          >
            <View
              style={{
                justifyContent: "center",
                alignItems: "center",
                marginTop: 80,
                height: 200,
              }}
            >
              <Image
                source={require("../../assets/download-removebg-preview.png")}
                style={{resizeMode: "contain", height: "100%", width: "100%" }}
              />
            </View>
          </View>

          

          <Modal animationType="slide" 
           transparent visible={isModalVisible_two} 
           presentationStyle="overFullScreen" 
           onDismiss={toggleModalVisibility}>
            <View style={styles_dialog.viewWrapper}>

              <View style={styles_dialog.modalView}>
                <LinearGradient colors={['rgb(170, 152, 169)', 'transparent']} >
                  <View
                    style={{flexDirection: 'row',width:'100%'}}>
                     
                      <TouchableOpacity onPress={() => {toggleModalVisibilityTwo()}} style={{marginLeft:'auto',marginRight:5,padding:5}}>
                        <FontAwesome5Icon
                          name="times"
                          
                          size={25}
                          color="black"
                        />
                      </TouchableOpacity>
                  </View>

                  <View style={stylesnew.container}>
                    <Text style={stylesnew.paragraph}>
                      You are just one step away!
                    </Text>
                    <Text style={stylesnew.paragraphTwo}>
                      Enter Business Email Id
                    </Text>
                    <View style={{ flex: 1 }}>
                      {emailError.length > 0 &&
                        <Text style={stylesnew.paragraphError}>{emailError}</Text>
                      }
                      <Text style={{ color: "red", alignSelf: "center" }}>{error}</Text>
                      <Input
                        placeholder="Email"
                        leftIcon={
                          <FontAwesome5Icon
                            style={styles.icon}
                            name="user"
                            size={24}
                            color="black"
                          />
                        }
                        value={demoEmail}
                        inputContainerStyle={{
                          marginVertical: 0,
                          borderColor: "black",
                          backgroundColor: "white",
                          borderRadius: 2,
                        }}
                        errorMessage=""
                        autoCapitalize='none'
                        onChangeText={(username) => setDemoEmail(username)}
                      />
                
                      <View style={{ marginTop: 50, marginHorizontal: 70 }}>
                      <TouchableOpacity onPress={hit_go_demo}>
                        <LinearGradient
                          // Button Linear Gradient
                          colors={['#6b4661', '#4f3347', '#452d3e']}
                          style={styles.button}>
                          
                            <Text style={styles.text}>Check Demo</Text>
                          
                        
                        </LinearGradient>
                      </TouchableOpacity>
                      </View>


                      <View style={{ marginTop: 50, marginHorizontal: 70,alignSelf: "center" ,fontWeight:"bold" }}>
                        <Pressable  onPress={move_to_create_account_page} >
                          <Text style={{marginTop:3,fontWeight:"bold",fontSize:16 }} hitSlop={{top: 20, bottom: 20, left: 50, right: 50}} > Create Account</Text>
                        </Pressable>
                      </View>

                    </View>


                  </View>


                </LinearGradient>
              </View>
              
            </View>
          </Modal>



          <View style={{ flex: 1 }}>
            <View style={{ marginHorizontal: 30,marginVertical : 40 }}>
              <Text style={{ color: "red", alignSelf: "center" }}>{error}</Text>
              <Input
                placeholder="Email"
                leftIcon={
                  <FontAwesome5Icon
                    style={styles.icon}
                    name="user"
                    size={24}
                    color="black"
                  />
                }
                value={values.username}
                inputContainerStyle={{
                  marginVertical: 10,
                  borderColor: "black",
                  backgroundColor: "white",
                  borderRadius: 2,
                  height : 60
                }}
                errorMessage=""
                autoCapitalize='none'
                onChangeText={(username) => setValues({ ...values, username })}
              />
              <PasswordInputText
                secureTextEntry={true}
                style={{ marginTop: 1, marginHorizontal: 10 }}
                leftIcon={
                  <FontAwesome5Icon
                    name="lock"
                    style={styles.icon}
                    size={24}
                    color="black"
                  />
                }
                value={values.password}
                inputStyle={{
                  color: "black",
                }}
                inputContainerStyle={{
                  marginVertical: 10,
                  borderColor: "black",
                  backgroundColor: "white",
                  borderRadius: 2,
                }}
                errorMessage=""
                onChangeText={(password) => setValues({ ...values, password })}
              />
            </View>
            <View style={{ marginTop: 20, marginHorizontal: 40 }}>
              <Button
                raised
                loading={isLoading}
                title="LOGIN"
                onPress={fetchDbName}
                buttonStyle={{ backgroundColor: "#6b4661" }}
              />
            </View>

            <View style={{ marginTop: 20, marginHorizontal: 40,display: 'none' }}>
              <Button
                raised
                loading={isLoading}
                title="LOGIN"
                onPress={fetchDbName1}
                buttonStyle={{ backgroundColor: "#6b4661" }}
              />
            </View>


            <View style={{ marginTop: 20, marginHorizontal: 40 }}>
            

            </View>


          </View>
        </View>
       
      </ScrollView>
       </ImageBackground>
    </View>
  );
};

const stylesnew = StyleSheet.create({
  container: {
    flex: 1,
    textAlign: 'center',
    padding: 9,
    paddingTop:height * 0.10,
  },
  paragraph: {
    margin: '3%',
    marginBottom:'10%',
    fontSize: 25,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  paragraphTwo: {
    marginTop: 4,
    marginLeft: '3%',
    fontSize: 16,
    fontWeight: 'bold',
    
  },
  paragraphError: {
    marginTop: 4,
    marginLeft: '3%',
    fontSize: 16,
    fontWeight: 'bold',
    color:"red",
    
  },
  paragraphThree: {
    marginTop: '22%',
    marginLeft: '3%',
    fontSize: 16,
    fontWeight: 'bold',
    
  },
});


const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    backgroundColor: "#FFFFFF",
  },
  icon: {
    marginHorizontal: 10,
    marginLeft: -5
  },
  button: {
    padding: 10,
    alignItems: 'center',
    borderRadius: 5,
  },
  text: {
    backgroundColor: 'transparent',
    fontSize: 15,
    color: '#fff',
  },
});

const styles_dialog = StyleSheet.create({
  screen: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: "#fff",
  },
  viewWrapper: {
      flex: 1,
      alignItems: "center",
      justifyContent: "center",
      backgroundColor: "rgba(0, 0, 0, 0.2)",
  },
  modalView: {
    flex:1,
      alignItems: "center",
      justifyContent: "center",
      position: "absolute",
      top: "15%",
      left: "45%",
      elevation: 5,
      transform: [{ translateX: -(width * 0.4) }, 
                  { translateY: -90 }],
      height: height * 0.9,
      width: width * 0.9,
      backgroundColor: "#fff",
      borderRadius: 10,
  },
  textInput: {
      width: "80%",
      borderRadius: 5,
      paddingVertical: 8,
      paddingHorizontal: 16,
      borderColor: "rgba(0, 0, 0, 0.2)",
      borderWidth: 1,
      marginBottom: 8,
  },
});
export default Login;
