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
  ActivityIndicator
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
    url: "https://ri-fx.erp.techtime.me",
    username: "",
    password: "",
  });
  // AsyncStorage.getItem('username').then((value) => this.setState({ 'username': values.username }))
  const [isLoading, setIsLoading] = useState(false);
  const [demoEmail, setDemoEmail] = useState("");
  const image = "../../assets/a_CRM.png";
  const [error, setError] = useState("");
  var [isSelected, setSelection] = useState(false);
  const [stop, setStop] = useState(false);
  const [show_view, set_show_view] = useState(false);
  const [isModalVisible, setModalVisible] = useState(false);
  const [isModalVisible_two, setModalVisibleTwo] = useState(false);
  const [selected_db, setDB] = useState("");
  // const [data_url, setData_url] = useState("");


 const _retrieveData = async () => {

  console.log("I am inside retrieveData method")
  try {
      values.username = await AsyncStorage.getItem('username');
      values.password = await AsyncStorage.getItem('password');
      console.log("values.username******",values.username);
      console.log("values.password******",values.password)
      if (values.username && values.password){
        set_show_view(true);
        fetchDbName(values.url); 
      }
    }
  catch (error) {

    console.log("I am inside catch ++++++++++++++++++++++")
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
    console.log("Hello Hello!")
    setModalVisible(!isModalVisible);
  };

  const toggleModalVisibilityTwo = () => {
    console.log("Hello Hello!")
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
    console.log("Test************",demoEmail);
    var values1 = {
      'url' : 'ri-fx.erp.techtime.me',
      'username': demoEmail,
      'password': '1234'
    }
    navigation.navigate("Home", { values : values1, database: "odoo15appsnew" });

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

  const fetchDbName = async(urlvalue) => {
  setIsLoading(true);
    if (values.username && values.password){
    console.log("urlvalue@@@@@@@@@@");
      var url1 = 'https://ri-fx.erp.techtime.me/membership/login/details/odoo/mobile'
      axios
      .get(url1,
        {
        params: {
          email : values.username.trim().toLowerCase(),
        },
        })
        .then((response) => {
            const data_url = response.data.db_url;
            //setData_url(response.data.db_url);
           // console.log("response.data.app_id*************",response.data);
            if (response.data.membership == 1){
              if (response.data.expired == 0){
                if (response.data.draft == 0){

                  axios
                    .post(`https://${data_url}/web/database/list`, {
                      params: {
                        pass: "supervisor351",
                      },
                    })
                    .then((response) => {
                      // console.log("databasefor demourl@@@@@@@@@123",response.data.result);
                      console.log("databasefor demourl@@@@@@@@@",response.data.result[0]);
                      // let database_array_length = response.data.result.length;
                      // console.log("database_array_length*******",database_array_length);


                      var dbvalue = response.data.result[0];
                      var dct = {
                        'dbvalue' : dbvalue,
                        'data_url' : data_url,
                        'username' : values.username.trim(),
                        'password' : values.password
                      }
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
                      setIsLoading(false);
                      alert("Invalid Crendentials!");
                    });
                }
                else if (response.data.draft == 1){
                  setIsLoading(false);
                  alert("Please Contact Support !");

                }  
              }
            else if(response.data.expired == 1){
              setIsLoading(false);
              alert("Membership Expired ! Please Pay on time. ");    
            }


            }
            else if(response.data.membership == 0){
              setIsLoading(false);
              alert("Your subscription is not valid");    
            }
            else{
              setIsLoading(false);
              alert("Your subscription having Some Issues!");
            }            
        })
        .catch((e) => {
          alert("Kindly Signup!")
        setIsLoading(false);
        });
      }
       else{
        if(!stop){
          console.log("stop******",stop);
          alert("please enter valid credential!");
          setIsLoading(false);
        }
       }

};

  const handleLogin = (dct) => {
    console.log("data_url@@@@@@@@@@@",dct);
    const url = `https://${dct.data_url}/web/session/authenticate`;
    console.log("data_url1111@@@@@@@@@@@",url);
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
        console.log("data.result.db*****",data.result.db);



        if (data.result.db == dct.dbvalue) {
          setIsLoading(false);
          console.log("dct.dbvalue@@@@@@@",dct.dbvalue);
          var values1 = {
            'url' : dct.data_url,
            'username': dct.username,
            'password': dct.password
          }
          AsyncStorage.setItem('username', dct.username);
          AsyncStorage.setItem('password', dct.password);
          console.log("values1@@@@@@@@@@@@@",values1,dct.dbvalue)
          navigation.navigate("Home", { values : values1, database: dct.dbvalue });
        } else {
          setIsLoading(false);
        }
      })
      .catch((e) => {
        setIsLoading(false);
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
                source={require("../../assets/a_CRM.png")}
                style={{resizeMode: "contain", height: "100%", width: "100%" }}
              />
            </View>
          </View>

          <Modal animationType="slide" 
           transparent visible={isModalVisible} 
           presentationStyle="overFullScreen" 
           onDismiss={toggleModalVisibility}>
            <View style={styles_dialog.viewWrapper}>
              <View style={styles_dialog.modalView}>
                <View
                  style={{flexDirection: 'row',width:'100%'}}>
                   
                    <TouchableOpacity onPress={() => {toggleModalVisibility()}} style={{marginLeft:'auto',marginRight:5}}>
                      <FontAwesome5Icon
                        name="times"
                        
                        size={20}
                        color="black"
                      />
                    </TouchableOpacity>
                </View>

                <View style={stylesnew.container}>
                  <Text style={stylesnew.paragraph}>
                    Kindly Select The Database
                  </Text>
                  <DropDownPicker
                      items={[
                          {label: 'odoo14apps', value: 'odoo14apps'},
                          {label: 'odoo14appsnew', value: 'odoo14appsnew'},
                      ]}
                      defaultIndex={0}
                      containerStyle={{height: 40}}
                      onChangeItem={item => setDB(item.value)}
                  />
                </View>

                <View style={{ marginTop: 20, marginHorizontal: 40 }}>
                  <Button
                    title="    Go    "
                    onPress={hit_go}
                    buttonStyle={{ backgroundColor: "#6b4661" }}
                  />
                </View>

              </View>
            </View>
          </Modal>


          <Modal animationType="slide" 
           transparent visible={isModalVisible_two} 
           presentationStyle="overFullScreen" 
           onDismiss={toggleModalVisibility}>
            <View style={styles_dialog.viewWrapper}>
              <View style={styles_dialog.modalView}>
                <View
                  style={{flexDirection: 'row',width:'100%'}}>
                   
                    <TouchableOpacity onPress={() => {toggleModalVisibilityTwo()}} style={{marginLeft:'auto',marginRight:5}}>
                      <FontAwesome5Icon
                        name="times"
                        
                        size={20}
                        color="black"
                      />
                    </TouchableOpacity>
                </View>

                <View style={stylesnew.container}>
                  <Text style={stylesnew.paragraph}>
                    Kindly Enter The Email Id
                  </Text>
          <View style={{ flex: 1 }}>
            
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
                  marginVertical: 10,
                  borderColor: "black",
                  backgroundColor: "white",
                  borderRadius: 2,
                }}
                errorMessage=""
                autoCapitalize='none'
                onChangeText={(username) => setDemoEmail(username)}
              />
              
              </View>
                </View>

                <View style={{ marginTop: 20, marginHorizontal: 40 }}>
                  <Button
                    title="    Go    "
                    onPress={hit_go_demo}
                    buttonStyle={{ backgroundColor: "#6b4661" }}
                  />
                </View>

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
                }}
                errorMessage=""
                autoCapitalize='none'
                onChangeText={(username) => setValues({ ...values, username })}
              />
              <PasswordInputText
                secureTextEntry={true}
                leftIcon={
                  <FontAwesome5Icon
                    name="lock"
                    style={styles.icon}
                    size={24}
                    color="black"
                  />
                }
                value={values.password}
                placeholder="Password"
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

            <View style={{ marginTop: 20, marginHorizontal: 40}}>
              <Button
                raised
                loading={isLoading}
                title="Demo"
                onPress={requestDemo}
                buttonStyle={{ backgroundColor: "#6b4661" }}
              />
            </View>            

            <View style={{ marginTop: 20, marginHorizontal: 40 }}>
            <TouchableOpacity onPress={() => navigation.navigate("Signup")}>
              <Text
                style={{
                  alignSelf: "center",
                  marginTop: 20,
                  fontSize: 19,
                  color: "white",
                  display:"none"
                }}
              >
                Don't have an account?
              </Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => navigation.navigate("Demo")}>
              <Text
                style={{
                  alignSelf: "center",
                  marginTop: 15,
                  fontSize: 15,
                  color: "white",
                }}
              >
                Create Account
              </Text>
            </TouchableOpacity>

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
    padding: 8,
  },
  paragraph: {
    margin: 24,
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
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
      top: "30%",
      left: "50%",
      elevation: 5,
      transform: [{ translateX: -(width * 0.4) }, 
                  { translateY: -90 }],
      height: height * 0.4,
      width: width * 0.8,
      backgroundColor: "#fff",
      borderRadius: 7,
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
