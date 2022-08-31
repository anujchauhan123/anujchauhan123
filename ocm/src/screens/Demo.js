import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  KeyboardAvoidingView,
  Image,
  ImageBackground,
  StatusBar, 
  TouchableOpacity,
  Alert,
  Platform,
  ScrollView
} from "react-native";
import { WebView } from "react-native-webview";
import axios from "axios";
import {Picker} from "@react-native-picker/picker";
import FontAwesome5Icon from "@expo/vector-icons/FontAwesome5";
import { Input, Button } from "react-native-elements";
import * as SecureStore from "expo-secure-store";
import CheckBox from 'react-native-check-box';
//import { ScrollView } from "react-native-gesture-handler";
import { KeyboardAwareScrollView } from 'react-native-keyboard-aware-scroll-view';
import {widthPercentageToDP as wp, heightPercentageToDP as hp} from 'react-native-responsive-screen';
import {
  requestTrackingPermissionsAsync,
  getTrackingPermissionsAsync,
  isAvailable
} from 'expo-tracking-transparency';
import CountryPicker, { getAllCountries, getCallingCode } from 'react-native-country-picker-modal';
import { getTrackingStatus } from 'react-native-tracking-transparency';

// console.log("checking@@@@@@@@@@")

const Demo = ({ navigation }) => {
  const [values1, setValues] = useState({
    url: "https://ri-fx.erp.techtime.me",
    company_name:"",
    username:"",
    email: "",
    odoo_url:"",
    mem_code:"",
    phone: "",
    calling_code:"1",
    countryCode:"",
    company_size:"",
    interest:"",
    currency:"USD",
    timezone:"",
  });
  const [countryCode, setCountryCode] = useState('US');
  const [country, setCountry] = useState('United States');
  const [callingCode, setcallingCode] = useState("1");
  const [deviceType, setDeviceType] = useState("Android");
  const [withCallingCodeButton, setWithCallingCodeButton] = useState(true);
  const [withLanguage, setWithLanguage] = useState(true);
  const [email_value, setEmailValue] = useState("");
  const [withFlag, setWithFlag] = useState(true);
  const [withEmoji, setWithEmoji] = useState(true);
  const [withFilter, setWithFilter] = useState(true);
  const [withAlphaFilter, setWithAlphaFilter] = useState(true);
  const [withCallingCode, setWithCallingCode] = useState(true);
  var [isSelected, setSelection] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [url, setUrl] = useState("");
  const [isEmailIn, setisEmailIn] = useState(false);
  //const [isEmailType, setisEmailType] = useState(false);
  const [isEmailType, setisEmailType] = useState(true);

const onSelect = (country) => {
    //console.log("country@@@@@@@@@@@@@@@@",country);
    setCountryCode(country.cca2);
    setCountry(country);
    var countrycode = JSON.stringify(country, null, 2);
    console.log("countrycode@@@@@@@@@@@@@@@@",countrycode);
    console.log("callingCode*****************",callingCode);
    console.log("callingCode*****************",country);
    // err

    
  }

  const  handleEmail = (email) => {
      // console.log("values1.username******",values1.username);
      // console.log("values1.company******",values1.company_name);
      // console.log("values1.phone******",values1.phone);
      setValues({ email: email,
                  username: values1.username,
                  company_name : values1.company_name,
                  phone: values1.phone,
                  odoo_url: values1.odoo_url,

                 });
      // setEmailValue(email);
   }

  const changing_checkbox = (urlvalue) => {
    if (isSelected){
      setSelection(false);
    }else{
      setSelection(true);
    }
  };
  const _navigate_to_login = () => {
    navigation.navigate("Login");
  };

  // const fetchDbN = () => {
  //   console.log("Platform.OS********",Platform.OS);

  // };
  const hit_go_demo = () => {
    
    var values2 = {
      'url' : 'ri-fx.erp.techtime.me',
      'username': values1.email.trim().toLowerCase(),
      'password': '1234'
    }
    navigation.navigate("Home", { values : values2, database: "odoo15appsnew" });
  };
  
  const fetchDbN123 = () => {
    // let re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    // //console.log("re.test(values1.email)******",re.test(values1.email));

    // if ( !re.test(values1.email) ) {
    //   alert("test**********",re.test(values1.email));
    //   return false;
    //     // this is a valid email address
    //     // call setState({email: email}) to update the email
    //     // or update the data in redux store.
    // }
  }
  const fetchDbN = () => {
    let re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

    setIsLoading(true);
      const mail = email_value;   
      if(values1.company_name.trim() && values1.phone.trim() && values1.username.trim() && (re.test(values1.email)) &&  values1.odoo_url.trim() && values1.mem_code.trim() && isSelected){
        // var RandomNumber = Math.floor(Math.random() * 1000) + 1 ;
        // var randomChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        // var result = '';
        // for ( var i = 0; i < 5; i++ ) {
        //     result += randomChars.charAt(Math.floor(Math.random() * randomChars.length));
        // }
        // var password = result+RandomNumber
        //console.log("password@@@@@@@@@@@@@2",password);

      axios
      .post(`https://ri-fx.erp.techtime.me/membership/create`, {
        params: {
          username: values1.username,
          email : values1.email.trim().toLowerCase(),
          company : values1.company_name.trim(),
          phone: callingCode+values1.phone,
          //password: password,
          device_type:Platform.OS,
          country_name: country,
          country_code: countryCode,
          calling_code: callingCode,
          app_id : 1,
          odoo_mob_app:true,
          run_code:true,
          db_url:values1.odoo_url,
          mem_code:values1.mem_code,
        },
      })
      .then((response) => {
      setIsLoading(false);
      // console.log("response.data.message@@@@@@@@@@@@@@@@",response);
      var response_obj = JSON.parse(response.data.result);
      console.log("response_obj*******",response_obj);
      if (response_obj.message === "new_membership"){
        // const membership_name = response.data.membership_name
        // const user_id = response.data.user_id
        // var dbname = values1.username.replace(/ /g,'');
        // var user = dbname.toLowerCase();
        // var product = "";
        // if (selectedseValue === "Pro Edition"){
        //   product = "CrmDriveP";
        // }else if (selectedseValue === "Enterprise Edition"){
        //   product = "CrmDriveE";
        // }else{
        //   product = "CrmDriveB";
        // }
        // var database_url = "https://www.o2btechnologies.com/saas_portal/add_new_client/app?dbname="+user+"&plan_id=10&product_name="+product+"&membership_id="+membership_name+"&user_id="+user_id+"&password="+password+"&calling_code="+"1"+"&currency="+"USD"+"&country_code="+countryCode+"&tz="+"Asia/Kolkata"
        // let url = database_url;
        // setUrl(url);
        var show_msg = "Congratulations! You are now our Member."
        show_msg = response_obj.msg
        Alert.alert(
        "",
        show_msg,
        [
          { text: "OK", onPress: () => _navigate_to_login() },
          {text: 'Check Demo', onPress: () => hit_go_demo()},
        ],
        { cancelable: false }
        );


        // console.log("database_url@@@@@@@@@@@@@@",database_url);
        //navigation.navigate("Democrm", { values1, database: database_url });
      }
      else if (response_obj.message === "old_membership"){
        alert("This business email id already exist.");
      }
      else if (response_obj.message === "all_ready_exist_with_this_comp"){
        alert("This business email id already exist.");
      }

      })
      .catch((e) => {
      setIsLoading(false);
      //console.log("e***********",e);
       alert("Something Went Wrong! "+e);
      });
    }
    else{
      setIsLoading(false);
      if ((!values1.company_name) || values1.company_name.trim().length == 0 ){
        alert("Company Name is Missing !");
        return false;
      }
      if ((!values1.username) || values1.username.trim().length == 0){
        alert("Forget to enter Your Name!");
        return false;
      }
      if ((!values1.phone) || values1.phone.trim().length == 0){
        alert("Phone Number is Missing!");
        return false;
      }
      if ((!values1.email) || values1.email.trim().length == 0){
        alert("Your Email is Missing!");
        return false;
      }
      if ( !re.test(values1.email) ) {
        alert("Email is Invalid!");
        return false;
      }
      if ((!values1.odoo_url) || values1.odoo_url.trim().length == 0){
        alert("Your Odoo Url is Missing!");
        return false;
      }
      if ((!values1.mem_code) || values1.mem_code.trim().length == 0){
        alert("Your Mem Code is Missing!");
        return false;
      }

      if (!isSelected){
        alert("I am afraid ! Your didn't agree to our Terms & Condition!");
        return false;
      }
    }
  };
  return (

    <View style={styles.container}>
          <KeyboardAwareScrollView  keyboardShouldPersistTaps={'always'}
              style={{flex:1}}
              showsVerticalScrollIndicator={false}>
      <ScrollView>
      <ImageBackground source={require("../../assets/pexels-photo.jpeg")}
        style={{ height: hp('100%') }}>
      <StatusBar backgroundColor={"#84563f"} barStyle="light-content"></StatusBar>
      

          <View style={{ flex: 1 }}>
            <View style={{ marginHorizontal: 30 }}>
              <WebView
                  source={{
                    uri: url,
                  }}
                />
              <Text style={{ color: "red", alignSelf: "center" }}>{error}</Text>
              <Text
                style={{
                  marginTop: 15,
                  fontSize: 30,
                  color: "white",
                }}
              >
                Create an account
              </Text>
              <Text
                  style={{
                    marginTop: 20,
                    fontSize: 18,
                    color: "white",
                  }}
                >
                Company Name: <Text style={{color:"red"}}>*</Text>
              </Text>

              <Input
                placeholder="Your Company"
                value={values1.company_name}
                inputContainerStyle={{
                  marginVertical: 0,
                  marginLeft:-10,
                  borderColor: "white",
                  backgroundColor: "white",
                  paddingLeft:5,
                  borderRadius: 2,
                }}
                autoCapitalize='none'
                errorMessage=""
                onChangeText={(company_name) => setValues({ ...values1, company_name })}
              />              
              <Text
                  style={{
                    marginTop: 10,
                    fontSize: 18,
                    color: "white",
                  }}
                >
                  Name: <Text style={{color:"red"}}>*</Text>
              </Text>

              <Input
                value={values1.username}
                placeholder="Your Name"
                inputStyle={{
                  color: "black",
                }}
                inputContainerStyle={{
                  marginVertical: 5,
                  marginLeft:-10,
                  borderColor: "white",
                  backgroundColor: "white",
                  paddingLeft:5,
                  borderRadius: 2,
                }}
                errorMessage=""
                onChangeText={(username) => setValues({ ...values1, username })}
              />
              <Text
                  style={{
                    marginTop: 10,
                    fontSize: 18,
                    color: "white",
                  }}
                >
                Phone Number: <Text style={{color:"red"}}>*</Text>
              </Text>
              <Input
                leftIcon={
                  <CountryPicker
                  countryCode={countryCode}
                  withFilter
                  withFlag={true}
                  visible={false}
                  withCountryNameButton={false}
                  withCurrencyButton={false}
                  withAlphaFilter={false}
                  withCallingCodeButton
                  withCallingCode
                  withEmoji
                  placeholderTextColor="white"
                  style={{color:"white"}}
                  onSelect={country=>{
                    setCountry(country.name);
                    setCountryCode(country.cca2);
                    setcallingCode(country.callingCode[0]); 
                  }}
                  containerButtonStyle={{
                    marginLeft:-15,
                    color:"white",
                  }}                
              />
                }
                value={values1.phone}
                placeholder="Phone Number"
                keyboardType="numeric"
                inputStyle={{
                  color: "black",
                }}
                inputContainerStyle={{
                  marginVertical: 5,
                  marginLeft:-10,
                  borderColor: "white",
                  backgroundColor: "white",
                  borderRadius: 2,
                }}
                errorMessage=""
                onChangeText={(phone) => setValues({ ...values1, phone })}
              />
              <Text
                  style={{
                    marginTop: 10,
                    fontSize: 18,
                    color: "white",
                  }}
                >
                Email: <Text style={{color:"red"}}>*</Text>
              </Text>
              <Input
                placeholder="Your Email"
                leftIcon={
                  <FontAwesome5Icon
                    style={styles.icon}
                    name="paper-plane"
                    size={24}
                    color="black"
                  />
                }
                value={values1.email}
                errorMessage=""
                inputContainerStyle={{
                  marginVertical: 5,
                  marginLeft:-10,
                  borderColor: "white",
                  backgroundColor: "white",
                  paddingRight:10,
                  borderRadius: 2,
                }}
                autoCapitalize='none'
                onChangeText={handleEmail}
              />


              <Text
                  style={{
                    marginTop: 10,
                    fontSize: 18,
                    color: "white",
                  }}
                >
                  Odoo Url: <Text style={{color:"red"}}>*</Text>
              </Text>
              <Input
                placeholder="Odoo Url"
                leftIcon={
                  <FontAwesome5Icon
                    style={styles.icon}
                    name="globe"
                    size={24}
                    color="black"
                  />
                }
                value={values1.odoo_url}
                errorMessage=""
                inputContainerStyle={{
                  marginVertical: 5,
                  marginLeft:-10,
                  borderColor: "white",
                  backgroundColor: "white",
                  paddingRight:10,
                  borderRadius: 2,
                }}
                autoCapitalize='none'
                onChangeText={(odoo_url) => setValues({ ...values1, odoo_url})}
              />

              <Text
                  style={{
                    marginTop: 10,
                    fontSize: 18,
                    color: "white",
                  }}
                >
                  Mem Code:<Text style={{color:"red"}}> *</Text>
              </Text>
              <Input
                placeholder="Mem Code"
                
                value={values1.mem_code}
                errorMessage=""
                inputContainerStyle={{
                  marginVertical: 5,
                  marginLeft:-10,
                  borderColor: "white",
                  backgroundColor: "white",
                  paddingRight:10,
                  paddingLeft:5,
                  borderRadius: 2,
                }}
                onChangeText={(mem_code) => setValues({ ...values1, mem_code})}
              />



            </View>
            <View style={{paddingLeft: 30,marginTop:'4%'}}>
               <CheckBox
                  
                  onClick={()=>{
                    changing_checkbox()
                  }}
                  checkBoxColor={"white"}
                  rightTextStyle={{color:"white"}}
                  isChecked={isSelected}
                  rightText={"Terms & Conditions"}
              />
            </View>
              

            <View style={{ marginTop: '6%',marginHorizontal: 40 }}>
              <Button
                raised
                loading={isLoading}
                title="Submit"
                onPress={fetchDbN}
                buttonStyle={{ backgroundColor: "#6b4661"}}
              />
            </View>
            <View style={{marginTop:'4%'}}>
            <TouchableOpacity onPress={() => navigation.navigate("Login")}>
              <Text
                style={{
                  alignSelf: "center",
                  fontSize: 16,
                  color: "white",
                }}
              >
                Already Have an account?
              </Text>
            </TouchableOpacity>
            </View>
          </View>
      
      
      </ImageBackground>
      </ScrollView>
      </KeyboardAwareScrollView>
    </View>
    
  );
};
const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    backgroundColor: "#fff",
  },
  icon: {
    marginHorizontal: 10,
    marginLeft:-10
  },
});
export default Demo;