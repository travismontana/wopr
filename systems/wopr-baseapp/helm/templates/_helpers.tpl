{{/*
Expand the name of the chart.
*/}}
{{- define "wopr-baseapp.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "wopr-baseapp.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "wopr-baseapp.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "wopr-baseapp.labels" -}}
helm.sh/chart: {{ include "wopr-baseapp.chart" . }}
{{ include "wopr-baseapp.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "wopr-baseapp.selectorLabels" -}}
{{- if .Values.app.name }}
app.kubernetes.io/name: {{ .Values.app.name }}
{{- end }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Service Name
*/}}
{{- define "wopr-baseapp.serviceName" -}}
{{- default (include "wopr-baseapp.name" .) .Values.service.name }}
{{- end }}

{{/*
Service Protocol
*/}}
{{- define "wopr-baseapp.serviceProtocol" -}}
{{- default "TCP" .Values.service.protocol }}
{{- end }}

wopr-baseapp.serviceProtocol