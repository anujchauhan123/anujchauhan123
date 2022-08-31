// This is responsible for hide and show password option in login page, please update the code on path in node modules
// node_modules/react-native-hide-show-password-input/src/component/passwordInput.js
// according to this file if any issue in view.
import React, { useState } from "react";
import { View, StyleSheet } from "react-native";
import Icon from "react-native-vector-icons/MaterialIcons";
import PropTypes from "prop-types";
import { TextField } from "react-native-material-textfield";
import { Input, Button } from "react-native-elements";
const PasswordInputText = ({
  iconSize,
  iconColor,
  label,
  style,
  getRef,
  ...rest
}) => {
  const [eyeIcon, setEyeIcon] = useState("visibility-off");
  const [isPassword, setIsPassword] = useState(true);

  const changePwdType = () => {
    setEyeIcon(isPassword ? "visibility" : "visibility-off");
    setIsPassword((prevState) => !prevState);
  };

  const passReference = (ref) => {
    if (getRef) getRef(ref);
  };

  return (
    <View style={style}>
      <Input
        {...rest}
        ref={passReference}
        secureTextEntry={isPassword}
      />
      <Icon
        style={styles.icon}
        name={eyeIcon}
        size={iconSize}
        color={iconColor}
        onPress={changePwdType}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  icon: {
    position: "absolute",
    top: 20,
    right: 10,
  },
});

PasswordInputText.defaultProps = {
  iconSize: 25,
  label: "Password",
  iconColor: "#222222",
};

PasswordInputText.propTypes = {
  iconSize: PropTypes.number,
  label: PropTypes.string,
  iconColor: PropTypes.string,
};

export default PasswordInputText;
