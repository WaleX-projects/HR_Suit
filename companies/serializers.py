from rest_framework import serializers
from .models import Company, CompanySettings



class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = "__all__"
        read_only_fields = ["email", "phone"]
        
        


class CompanySettingsSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name")
    email = serializers.EmailField(source="company.email")
    phone = serializers.CharField(source="company.phone", allow_blank=True)
    address = serializers.CharField(source="company.address", allow_blank=True)
    country = serializers.CharField(source="company.country")
    timezone = serializers.CharField(source="company.timezone")

    class Meta:
        model = CompanySettings
        fields = [
            "company_name",
            "email",
            "phone",
            "address",
            "country",
            "timezone",
            "date_format",
            "working_days",
        ]

    def update(self, instance, validated_data):
        # 🔹 Update Company fields
        company_data = validated_data.pop("company", {})
        company = instance.company

        for attr, value in company_data.items():
            setattr(company, attr, value)
        company.save()

        # 🔹 Update Settings fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance        
 
 
 
 
"""
 
 {/*
        {/* ATTENDANCE SETTINGS - Keep your existing content */}
        <TabsContent value="attendance">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" /> Attendance Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Your existing attendance fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label>Standard Work Hours per Day</Label>
                  <Input 
                    type="number" 
                    value={settings.workHoursPerDay} 
                    onChange={(e) => updateSettings({ workHoursPerDay: parseInt(e.target.value) || 8 })} 
                  />
                </div>
                <div>
                  <Label>Late Arrival Grace Period (minutes)</Label>
                  <Input 
                    type="number" 
                    value={settings.lateArrivalGraceMinutes} 
                    onChange={(e) => updateSettings({ lateArrivalGraceMinutes: parseInt(e.target.value) || 15 })} 
                  />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Allow Late Arrivals</Label>
                  <p className="text-sm text-muted-foreground">Mark late instead of absent after grace period</p>
                </div>
                <Switch 
                  checked={settings.allowLateArrival} 
                  onCheckedChange={(checked) => updateSettings({ allowLateArrival: checked })} 
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Require Face Verification for Clock In</Label>
                </div>
                <Switch 
                  checked={settings.requireFaceVerification} 
                  onCheckedChange={(checked) => updateSettings({ requireFaceVerification: checked })} 
                />
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <Label>Enable Geo-Fencing</Label>
                </div>
                <Switch 
                  checked={settings.geoFencingEnabled} 
                  onCheckedChange={(checked) => updateSettings({ geoFencingEnabled: checked })} 
                />
              </div>

              <Button 
                onClick={() => saveSettings("Attendance")} 
                disabled={savingSection === "Attendance"}
              >
                {savingSection === "Attendance" ? "Saving..." : "Save Attendance Settings"}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* PAYROLL, ORGANIZATION, LEAVE, NOTIFICATIONS tabs remain the same as your original code */}

        {/* WORK LOCATION TAB */}
        <TabsContent value="work-location">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" /> My Work Location (Geo-fencing)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <p className="text-muted-foreground">
                Set your office or work location. This will be used during face attendance to verify you are within the allowed radius.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label>Latitude</Label>
                  <Input
                    type="number"
                    step="0.000001"
                    value={workLocation.latitude}
                    onChange={(e) => setWorkLocation({ ...workLocation, latitude: e.target.value })}
                    placeholder="6.524379"
                  />
                </div>
                <div>
                  <Label>Longitude</Label>
                  <Input
                    type="number"
                    step="0.000001"
                    value={workLocation.longitude}
                    onChange={(e) => setWorkLocation({ ...workLocation, longitude: e.target.value })}
                    placeholder="3.379206"
                  />
                </div>
              </div>

              <div>
                <Label>Allowed Radius (meters)</Label>
                <Input
                  type="number"
                  min={50}
                  max={500}
                  value={workLocation.radius}
                  onChange={(e) => setWorkLocation({ ...workLocation, radius: parseInt(e.target.value) || 100 })}
                />
              </div>

              <div className="flex gap-3">
                <Button 
                  onClick={getCurrentLocation} 
                  disabled={gettingLocation}
                  variant="outline"
                >
                  {gettingLocation ? "Getting Location..." : "📍 Get My Current Location"}
                </Button>

                <Button 
                  onClick={saveWorkLocation}
                  disabled={savingSection === "work-location" || !workLocation.latitude || !workLocation.longitude}
                >
                  {savingSection === "work-location" ? "Saving..." : "Save Work Location"}
                </Button>
              </div>

              {workLocation.latitude && workLocation.longitude && (
                <div className="p-4 bg-muted rounded-lg text-sm">
                  <p><strong>Saved Location:</strong></p>
                  <p>Lat: {workLocation.latitude} | Long: {workLocation.longitude}</p>
                  <p>Radius: {workLocation.radius} meters</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>  
        
        
"""             