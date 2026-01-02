#!/bin/bash
# publish-chart.sh
CHART_DIR="systems/wopr-baseapp/helm"
VERSION=$(grep '^version:' $CHART_DIR/Chart.yaml | awk '{print $2}')

helm package $CHART_DIR
helm push wopr-baseapp-${VERSION}.tgz oci://ghcr.io/travismontana/wopr/charts
