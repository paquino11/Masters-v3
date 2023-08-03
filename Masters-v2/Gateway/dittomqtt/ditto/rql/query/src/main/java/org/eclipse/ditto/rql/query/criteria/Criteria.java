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
package org.eclipse.ditto.rql.query.criteria;


import org.eclipse.ditto.rql.query.criteria.visitors.CriteriaVisitor;

/**
 * Search criteria.
 */
public interface Criteria {

    /**
     * Evaluates the search criteria by a visitor.
     *
     * @param <T> Result type of the evaluation.
     * @param visitor The visitor that performs the evaluation.
     * @return Result of the evaluation.
     */
    <T> T accept(CriteriaVisitor<T> visitor);
}
