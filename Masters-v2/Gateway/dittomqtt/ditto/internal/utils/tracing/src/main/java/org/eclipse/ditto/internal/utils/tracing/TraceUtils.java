/*
 * Copyright (c) 2017 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0
 *
 * SPDX-License-Identifier: EPL-2.0
 */
package org.eclipse.ditto.internal.utils.tracing;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

import javax.annotation.concurrent.Immutable;

import org.eclipse.ditto.base.model.headers.DittoHeaderDefinition;
import org.eclipse.ditto.internal.utils.metrics.DittoMetrics;
import org.eclipse.ditto.internal.utils.metrics.instruments.timer.PreparedTimer;

import akka.http.javadsl.model.HttpRequest;

/**
 * Utility for tracing Http requests.
 */
@Immutable
public final class TraceUtils {

    private static final String TRACING_FILTER_DELIMITER = "_";
    private static final String SLASH = "/";
    private static final Pattern DUPLICATE_SLASH_PATTERN = Pattern.compile("\\/+");

    private static final String HTTP_ROUNDTRIP_METRIC_NAME = "roundtrip_http";
    private static final String FILTER_AUTH_METRIC_NAME = "filter_auth";
    private static final String LIVE_CHANNEL_NAME = "live";
    private static final String TWIN_CHANNEL_NAME = "twin";
    private static final Pattern messagePattern = Pattern.compile("(.*/(inbox|outbox)/messages/.*)|(.*/inbox/claim)");

    private TraceUtils() {
        throw new AssertionError();
    }

    /**
     * Prepares an {@link PreparedTimer} with default {@link #HTTP_ROUNDTRIP_METRIC_NAME} and tags.
     *
     * @param request The request to extract tags and request method.
     * @return The prepared {@link PreparedTimer}
     */
    public static PreparedTimer newHttpRoundTripTimer(final HttpRequest request) {
        final String requestMethod = request.method().name();
        final String requestPath = request.getUri().toRelative().path();
        final String channel = determineChannel(request);

        final TraceInformation traceInformation = determineTraceInformation(requestPath);

        return newExpiringTimer(HTTP_ROUNDTRIP_METRIC_NAME)
                .tags(traceInformation.getTags())
                .tag(TracingTags.REQUEST_METHOD, requestMethod)
                .tag(TracingTags.CHANNEL, channel);
    }

    /**
     * Prepares an {@link PreparedTimer} with default {@link #FILTER_AUTH_METRIC_NAME} and tags.
     *
     * @param authenticationType The name of the authentication type (i.e. jwt, ...)
     * @return The prepared {@link PreparedTimer}
     */
    public static PreparedTimer newAuthFilterTimer(final CharSequence authenticationType) {
        return newAuthFilterTimer(authenticationType, new HashMap<>());
    }

    /**
     * Prepares an {@link PreparedTimer} with default {@link #FILTER_AUTH_METRIC_NAME} and tags.
     *
     * @param authenticationType The name of the authentication type (i.e. jwt, ...)
     * @param request The HttpRequest used to extract required tags.
     * @return The prepared {@link PreparedTimer}
     */
    public static PreparedTimer newAuthFilterTimer(final CharSequence authenticationType,
            final HttpRequest request) {
        final String requestPath = request.getUri().toRelative().path();

        final TraceInformation traceInformation = determineTraceInformation(requestPath);

        return newAuthFilterTimer(authenticationType, traceInformation.getTags());
    }

    private static PreparedTimer newAuthFilterTimer(final CharSequence authenticationType,
            final Map<String, String> requestTags) {

        Map<String, String> defaultTags = new HashMap<>();
        defaultTags.put(TracingTags.AUTH_SUCCESS, Boolean.toString(false));
        defaultTags.put(TracingTags.AUTH_ERROR, Boolean.toString(false));

        return newExpiringTimer(FILTER_AUTH_METRIC_NAME)
                .tags(requestTags)
                .tags(defaultTags)
                .tag(TracingTags.AUTH_TYPE, authenticationType.toString())
                .onExpiration(expiredTimer ->
                        expiredTimer
                                .tag(TracingTags.AUTH_SUCCESS, false)
                                .tag(TracingTags.AUTH_ERROR, true));
    }

    private static PreparedTimer newExpiringTimer(final String tracingFilter) {
        return DittoMetrics.timer(metricizeTraceUri(tracingFilter));
    }

    private static TraceInformation determineTraceInformation(final String requestPath) {
        final TraceUriGenerator traceUriGenerator = TraceUriGenerator.getInstance();
        return traceUriGenerator.apply(requestPath);
    }

    private static String determineChannel(final HttpRequest request) {
        // determine channel based on header or query parameter
        final boolean liveHeaderPresent = request.getHeader(DittoHeaderDefinition.CHANNEL.getKey())
                .filter(channelHeader -> LIVE_CHANNEL_NAME.equals(channelHeader.value()))
                .isPresent();
        final boolean liveQueryPresent = request.getUri().query().get(DittoHeaderDefinition.CHANNEL.getKey())
                .filter(LIVE_CHANNEL_NAME::equals)
                .isPresent();
        // messages are always live commands
        final String normalizePath = normalizePath(request.getUri().path());
        final boolean messageRequest = messagePattern.matcher(normalizePath).matches();

        return (liveHeaderPresent || liveQueryPresent || messageRequest) ? LIVE_CHANNEL_NAME : TWIN_CHANNEL_NAME;
    }

    /**
     * Replaces all characters that are invalid for metrics (at least for Prometheus metrics).
     */
    public static String metricizeTraceUri(final String traceUri) {
        return traceUri.replaceAll("[./:-]", TRACING_FILTER_DELIMITER);
    }

    /**
     * Normalizes the path and removes duplicate slashes.
     */
    public static String normalizePath(final String path) {
        if (path.isEmpty()) {
            return SLASH;
        }

        // remove duplicate slashes
        String normalized = DUPLICATE_SLASH_PATTERN.matcher(path).replaceAll(SLASH);

        // strip trailing slash if necessary
        if (normalized.length() > 1 && normalized.endsWith(SLASH)) {
            normalized = normalized.substring(0, normalized.length() - 1);
        }

        // add leading slash if necessary
        if (!normalized.startsWith(SLASH)) {
            normalized = SLASH + normalized;
        }

        return normalized;
    }

}
