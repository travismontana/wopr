{{/*
Expand the name of the chart.
*/}}
{{- define "wopr-config.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "wopr-config.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "wopr-config.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "wopr-config.labels" -}}
helm.sh/chart: {{ include "wopr-config.chart" . }}
{{ include "wopr-config.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "wopr-config.selectorLabels" -}}
app.kubernetes.io/name: {{ include "wopr-config.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "wopr-config.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "wopr-config.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Database connection URL
*/}}
{{- define "wopr-config.databaseUrl" -}}
/*postgresql://{{ .Values.postgresql.username }}:{{ .Values.postgresql.password }}@{{ include "wopr-config.fullname" . }}:5432/{{ .Values.postgresql.database }}*/
{{- .Values.postgresql.uri }}
{{- end }}
