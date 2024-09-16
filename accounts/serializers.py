from rest_framework import serializers
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only=True)
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password", "password2"]
        extra_kwargs = {
            "password":  {"write_only": True}
        }

    
    def validate_password(self, value):
        if len(value) < 6:
            raise ValueError({"Error": "Password is too short"})
        return value
    
    def validate_password2(self, value):
        if len(value) < 6:
            raise ValueError({"Error": "Password is too short"})
        return value

    

    def save(self):
        user = CustomUser(
            username = self.validated_data["username"],
            email = self.validated_data["email"],
            
        )
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError({"Error": "Both passwords must match"})
        
        user.set_password(password)
        user.save()
        return user